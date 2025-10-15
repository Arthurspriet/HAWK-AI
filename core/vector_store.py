"""
Vector store for HAWK-AI historical knowledge base.
Handles data ingestion from multiple sources (ACLED, CIA World Factbook),
embedding generation, and FAISS indexing.
"""
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import yaml
import json
import pickle
import pandas as pd
import numpy as np
import faiss
from tqdm import tqdm
from rich.console import Console
from sentence_transformers import SentenceTransformer

console = Console()


class VectorStore:
    """FAISS-based vector store for historical context."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize vector store."""
        self.config = self._load_config(config_path)
        self.store_path = Path(self.config['vector_store']['path'])
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        self.dimension = self.config['vector_store']['dimension']
        self.use_gpu = self.config['vector_store']['use_gpu']
        self.top_k = self.config['vector_store']['top_k']
        
        # Initialize embedding model (using sentence-transformers for compatibility)
        console.print("[cyan]Loading embedding model...[/cyan]")
        self.embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.dimension = self.embed_model.get_sentence_embedding_dimension()
        
        # Initialize or load FAISS index
        self.index = None
        self.documents = []
        self.metadata = []
        
        self._load_or_create_index()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        index_path = self.store_path / "faiss.index"
        docs_path = self.store_path / "documents.pkl"
        meta_path = self.store_path / "metadata.pkl"
        
        if index_path.exists() and docs_path.exists():
            console.print("[green]Loading existing vector index...[/green]")
            self.index = faiss.read_index(str(index_path))
            
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            with open(meta_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            console.print(f"[green]Loaded {len(self.documents)} documents[/green]")
        else:
            console.print("[yellow]Creating new vector index...[/yellow]")
            self._create_index()
    
    def _create_index(self):
        """Create new FAISS index."""
        if self.use_gpu and faiss.get_num_gpus() > 0:
            console.print("[cyan]Using GPU for FAISS index[/cyan]")
            res = faiss.StandardGpuResources()
            self.index = faiss.GpuIndexFlatL2(res, self.dimension)
        else:
            console.print("[cyan]Using CPU for FAISS index[/cyan]")
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def save_index(self):
        """Save index and documents to disk."""
        index_path = self.store_path / "faiss.index"
        docs_path = self.store_path / "documents.pkl"
        meta_path = self.store_path / "metadata.pkl"
        
        # Convert GPU index to CPU for saving
        if isinstance(self.index, faiss.GpuIndexFlat):
            cpu_index = faiss.index_gpu_to_cpu(self.index)
            faiss.write_index(cpu_index, str(index_path))
        else:
            faiss.write_index(self.index, str(index_path))
        
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        
        with open(meta_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        console.print(f"[green]Saved index with {len(self.documents)} documents[/green]")
    
    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]]):
        """Add documents to the vector store."""
        if len(texts) != len(metadata):
            raise ValueError("Number of texts and metadata must match")
        
        console.print(f"[cyan]Generating embeddings for {len(texts)} documents...[/cyan]")
        embeddings = self.embed_model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        
        # Normalize embeddings
        embeddings = embeddings.astype('float32')
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        self.documents.extend(texts)
        self.metadata.extend(metadata)
        
        console.print(f"[green]Added {len(texts)} documents to index[/green]")
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if top_k is None:
            top_k = self.top_k
        
        # Generate query embedding
        query_embedding = self.embed_model.encode([query], convert_to_numpy=True).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append({
                    "document": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(1 - dist)  # Convert distance to similarity
                })
        
        return results
    
    def ingest_acled_data(self, acled_path: Optional[str] = None):
        """Ingest ACLED CSV files into the vector store."""
        if acled_path is None:
            acled_path = "historical_context/ACLED"
        
        acled_dir = Path(acled_path)
        if not acled_dir.exists():
            console.print(f"[yellow]ACLED directory not found: {acled_path}[/yellow]")
            console.print("[yellow]Please place ACLED CSV files in data/historical_context/ACLED/[/yellow]")
            return
        
        csv_files = list(acled_dir.glob("*.csv"))
        if not csv_files:
            console.print(f"[yellow]No CSV files found in {acled_path}[/yellow]")
            return
        
        console.print(f"[cyan]Found {len(csv_files)} ACLED CSV files[/cyan]")
        
        all_texts = []
        all_metadata = []
        
        for csv_file in csv_files:
            console.print(f"[cyan]Processing {csv_file.name}...[/cyan]")
            
            try:
                df = pd.read_csv(csv_file, low_memory=False)
                console.print(f"  Loaded {len(df)} rows")
                
                # Create text representations
                for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
                    text = self._create_acled_text(row)
                    
                    # Handle both uppercase and lowercase column names
                    country = row.get('COUNTRY', row.get('country', 'Unknown'))
                    event_date = str(row.get('WEEK', row.get('YEAR', row.get('event_date', ''))))
                    event_type = row.get('EVENT_TYPE', row.get('event_type', ''))
                    
                    metadata = {
                        "source": "ACLED",
                        "source_file": csv_file.name,
                        "row_index": idx,
                        "country": country,
                        "event_date": event_date,
                        "event_type": event_type,
                    }
                    all_texts.append(text)
                    all_metadata.append(metadata)
                
            except Exception as e:
                console.print(f"[red]Error processing {csv_file.name}: {e}[/red]")
        
        if all_texts:
            console.print(f"[cyan]Adding {len(all_texts)} documents to vector store...[/cyan]")
            self.add_documents(all_texts, all_metadata)
            self.save_index()
        else:
            console.print("[yellow]No documents to add[/yellow]")
    
    def _create_acled_text(self, row: pd.Series) -> str:
        """Create searchable text from ACLED row."""
        parts = []
        
        # Handle both uppercase (aggregated data) and lowercase (event-level data) column names
        # Try uppercase first (aggregated data format)
        if 'WEEK' in row and pd.notna(row['WEEK']):
            parts.append(f"Week: {row['WEEK']}")
        elif 'YEAR' in row and pd.notna(row['YEAR']):
            parts.append(f"Year: {row['YEAR']}")
        elif 'event_date' in row and pd.notna(row['event_date']):
            parts.append(f"Date: {row['event_date']}")
        
        if 'REGION' in row and pd.notna(row['REGION']):
            parts.append(f"Region: {row['REGION']}")
        
        if 'COUNTRY' in row and pd.notna(row['COUNTRY']):
            parts.append(f"Country: {row['COUNTRY']}")
        elif 'country' in row and pd.notna(row['country']):
            parts.append(f"Country: {row['country']}")
        
        if 'ADMIN1' in row and pd.notna(row['ADMIN1']):
            parts.append(f"Admin Region: {row['ADMIN1']}")
        
        if 'EVENT_TYPE' in row and pd.notna(row['EVENT_TYPE']):
            parts.append(f"Event Type: {row['EVENT_TYPE']}")
        elif 'event_type' in row and pd.notna(row['event_type']):
            parts.append(f"Event Type: {row['event_type']}")
        
        if 'SUB_EVENT_TYPE' in row and pd.notna(row['SUB_EVENT_TYPE']):
            parts.append(f"Sub-Event: {row['SUB_EVENT_TYPE']}")
        elif 'sub_event_type' in row and pd.notna(row['sub_event_type']):
            parts.append(f"Sub-Event: {row['sub_event_type']}")
        
        if 'DISORDER_TYPE' in row and pd.notna(row['DISORDER_TYPE']):
            parts.append(f"Disorder Type: {row['DISORDER_TYPE']}")
        
        if 'EVENTS' in row and pd.notna(row['EVENTS']):
            parts.append(f"Number of Events: {row['EVENTS']}")
        
        if 'FATALITIES' in row and pd.notna(row['FATALITIES']):
            parts.append(f"Fatalities: {row['FATALITIES']}")
        elif 'fatalities' in row and pd.notna(row['fatalities']):
            parts.append(f"Fatalities: {row['fatalities']}")
        
        if 'POPULATION_EXPOSURE' in row and pd.notna(row['POPULATION_EXPOSURE']):
            parts.append(f"Population Exposure: {row['POPULATION_EXPOSURE']}")
        
        # Event-level data fields
        if 'actor1' in row and pd.notna(row['actor1']):
            parts.append(f"Actor 1: {row['actor1']}")
        
        if 'actor2' in row and pd.notna(row['actor2']):
            parts.append(f"Actor 2: {row['actor2']}")
        
        if 'location' in row and pd.notna(row['location']):
            parts.append(f"Location: {row['location']}")
        
        if 'notes' in row and pd.notna(row['notes']):
            notes = str(row['notes'])[:500]  # Truncate long notes
            parts.append(f"Notes: {notes}")
        
        return " | ".join(parts)
    
    def ingest_cia_facts_data(self, cia_facts_path: Optional[str] = None):
        """Ingest CIA World Factbook data into the vector store."""
        if cia_facts_path is None:
            cia_facts_path = "historical_context/CIA_FACTS"
        
        cia_facts_dir = Path(cia_facts_path)
        if not cia_facts_dir.exists():
            console.print(f"[yellow]CIA_FACTS directory not found: {cia_facts_path}[/yellow]")
            return
        
        # Look for JSON file first (preferred format)
        json_file = cia_facts_dir / "countries.json"
        csv_file = cia_facts_dir / "countries.csv"
        
        all_texts = []
        all_metadata = []
        
        if json_file.exists():
            console.print(f"[cyan]Processing CIA_FACTS JSON file...[/cyan]")
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                console.print(f"  Loaded {len(data)} countries")
                
                for country_name, country_data in tqdm(data.items(), desc="Processing countries"):
                    text = self._create_cia_facts_text(country_name, country_data)
                    metadata = {
                        "source": "CIA_FACTS",
                        "country": country_name,
                        "data_type": "country_profile",
                        "url": country_data.get('url', '')
                    }
                    all_texts.append(text)
                    all_metadata.append(metadata)
                    
            except Exception as e:
                console.print(f"[red]Error processing CIA_FACTS JSON: {e}[/red]")
        
        elif csv_file.exists():
            console.print(f"[cyan]Processing CIA_FACTS CSV file...[/cyan]")
            try:
                df = pd.read_csv(csv_file, low_memory=False)
                console.print(f"  Loaded {len(df)} countries")
                
                for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
                    if pd.notna(row.get('Country')):
                        text = self._create_cia_facts_text_from_csv(row)
                        metadata = {
                            "source": "CIA_FACTS",
                            "country": row.get('Country', 'Unknown'),
                            "data_type": "country_profile",
                            "url": row.get('url', '')
                        }
                        all_texts.append(text)
                        all_metadata.append(metadata)
                        
            except Exception as e:
                console.print(f"[red]Error processing CIA_FACTS CSV: {e}[/red]")
        else:
            console.print(f"[yellow]No CIA_FACTS data files found in {cia_facts_path}[/yellow]")
            return
        
        if all_texts:
            console.print(f"[cyan]Adding {len(all_texts)} country profiles to vector store...[/cyan]")
            self.add_documents(all_texts, all_metadata)
            self.save_index()
        else:
            console.print("[yellow]No documents to add from CIA_FACTS[/yellow]")
    
    def _create_cia_facts_text(self, country_name: str, country_data: Dict[str, Any]) -> str:
        """Create searchable text from CIA World Factbook country data."""
        parts = [f"Country: {country_name}"]
        
        # Priority fields for embedding
        priority_fields = [
            'Introduction: Background',
            'Geography: Location',
            'Geography: Area - total',
            'Geography: Climate',
            'Geography: Terrain',
            'Geography: Natural resources',
            'People and Society: Population - total',
            'People and Society: Ethnic groups',
            'People and Society: Languages',
            'People and Society: Religions',
            'Government: Government type',
            'Government: Capital - name',
            'Economy: Economic overview',
            'Economy: GDP (official exchange rate)',
            'Economy: Industries',
            'Economy: Agricultural products',
            'Military and Security: Military and security forces',
            'Terrorism: Terrorist group(s) - Terrorist group(s)',
            'Transnational Issues: Refugees and internally displaced persons - refugees (country of origin)',
        ]
        
        # Add priority fields
        for field in priority_fields:
            if field in country_data and country_data[field]:
                value = str(country_data[field])
                if len(value) > 1000:  # Truncate very long fields
                    value = value[:1000] + "..."
                parts.append(f"{field}: {value}")
        
        # Add any additional key fields not in priority list
        for key, value in country_data.items():
            if key not in priority_fields and key != 'url' and value:
                value_str = str(value)
                if len(value_str) <= 500:  # Only include shorter fields
                    parts.append(f"{key}: {value_str}")
        
        return " | ".join(parts)
    
    def _create_cia_facts_text_from_csv(self, row: pd.Series) -> str:
        """Create searchable text from CIA World Factbook CSV row."""
        parts = []
        
        # Priority columns
        priority_columns = [
            'Country',
            'Introduction: Background',
            'Geography: Location',
            'Geography: Area - total',
            'Geography: Climate',
            'People and Society: Population - total',
            'People and Society: Ethnic groups',
            'People and Society: Languages',
            'Government: Government type',
            'Government: Capital - name',
            'Economy: Economic overview',
            'Economy: Industries',
        ]
        
        for col in priority_columns:
            if col in row and pd.notna(row[col]):
                value = str(row[col])
                if len(value) > 1000:  # Truncate long text
                    value = value[:1000] + "..."
                parts.append(f"{col}: {value}")
        
        return " | ".join(parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "use_gpu": self.use_gpu,
        }


def main():
    """CLI for vector store management."""
    parser = argparse.ArgumentParser(description="HAWK-AI Vector Store Manager")
    parser.add_argument('--rebuild', action='store_true', help='Rebuild index from all data sources')
    parser.add_argument('--ingest-acled', action='store_true', help='Ingest ACLED data only')
    parser.add_argument('--ingest-cia-facts', action='store_true', help='Ingest CIA World Factbook data only')
    parser.add_argument('--stats', action='store_true', help='Show index statistics')
    parser.add_argument('--query', type=str, help='Test query')
    
    args = parser.parse_args()
    
    store = VectorStore()
    
    if args.rebuild:
        console.print("[yellow]Rebuilding vector index from all sources...[/yellow]")
        # Clear existing index
        store._create_index()
        store.documents = []
        store.metadata = []
        # Ingest all data sources
        console.print("\n[bold cyan]Ingesting ACLED data...[/bold cyan]")
        store.ingest_acled_data()
        console.print("\n[bold cyan]Ingesting CIA World Factbook data...[/bold cyan]")
        store.ingest_cia_facts_data()
        console.print("\n[bold green]✓ Rebuild complete![/bold green]")
    
    if args.ingest_acled:
        console.print("[yellow]Ingesting ACLED data...[/yellow]")
        store.ingest_acled_data()
    
    if args.ingest_cia_facts:
        console.print("[yellow]Ingesting CIA World Factbook data...[/yellow]")
        store.ingest_cia_facts_data()
    
    if args.stats:
        stats = store.get_stats()
        console.print("\n[bold]Vector Store Statistics:[/bold]")
        for key, value in stats.items():
            console.print(f"  {key}: {value}")
    
    if args.query:
        console.print(f"\n[bold]Searching for:[/bold] {args.query}")
        results = store.search(args.query)
        for i, result in enumerate(results, 1):
            console.print(f"\n[cyan]Result {i} (score: {result['score']:.3f}):[/cyan]")
            console.print(f"  {result['document'][:200]}...")
            console.print(f"  Metadata: {result['metadata']}")


if __name__ == "__main__":
    main()
