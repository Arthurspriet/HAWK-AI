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
        try:
            if self.use_gpu and hasattr(faiss, 'get_num_gpus') and faiss.get_num_gpus() > 0:
                console.print("[cyan]Using GPU for FAISS index[/cyan]")
                res = faiss.StandardGpuResources()
                self.index = faiss.GpuIndexFlatL2(res, self.dimension)
            else:
                console.print("[cyan]Using CPU for FAISS index[/cyan]")
                self.index = faiss.IndexFlatL2(self.dimension)
        except Exception:
            console.print("[cyan]Using CPU for FAISS index[/cyan]")
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def save_index(self):
        """Save index and documents to disk."""
        index_path = self.store_path / "faiss.index"
        docs_path = self.store_path / "documents.pkl"
        meta_path = self.store_path / "metadata.pkl"
        
        # Convert GPU index to CPU for saving (if GPU is available)
        try:
            if hasattr(faiss, 'GpuIndexFlat') and isinstance(self.index, faiss.GpuIndexFlat):
                cpu_index = faiss.index_gpu_to_cpu(self.index)
                faiss.write_index(cpu_index, str(index_path))
            else:
                faiss.write_index(self.index, str(index_path))
        except Exception:
            # Fall back to direct write if GPU conversion fails
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
    
    def ingest_wbi_data(self, wbi_path: Optional[str] = None):
        """Ingest World Bank Indicators data into the vector store."""
        if wbi_path is None:
            wbi_path = "historical_context/WBI"
        
        wbi_dir = Path(wbi_path)
        if not wbi_dir.exists():
            console.print(f"[yellow]WBI directory not found: {wbi_path}[/yellow]")
            console.print("[yellow]Please place WBI CSV files in historical_context/WBI/[/yellow]")
            return
        
        csv_files = list(wbi_dir.glob("*.csv"))
        if not csv_files:
            console.print(f"[yellow]No CSV files found in {wbi_path}[/yellow]")
            return
        
        console.print(f"[cyan]Found {len(csv_files)} WBI CSV files[/cyan]")
        
        # Map filenames to indicator names
        indicator_map = {
            'gdp.csv': 'GDP (current US$)',
            'gdp_growth.csv': 'GDP growth (annual %)',
            'gdp_per_capita.csv': 'GDP per capita (current US$)',
            'gdp_per_capita_growth.csv': 'GDP per capita growth (annual %)',
            'gdp_ppp.csv': 'GDP PPP (current international $)',
            'gdp_ppp_per_capita.csv': 'GDP PPP per capita (current international $)',
        }
        
        all_texts = []
        all_metadata = []
        
        for csv_file in csv_files:
            console.print(f"[cyan]Processing {csv_file.name}...[/cyan]")
            indicator_name = indicator_map.get(csv_file.name, csv_file.stem.replace('_', ' ').title())
            
            try:
                df = pd.read_csv(csv_file, low_memory=False)
                console.print(f"  Loaded {len(df)} countries")
                
                # Get year columns (skip 'Country Name', 'Code', and 'Unnamed' columns)
                year_columns = [col for col in df.columns 
                               if col not in ['Country Name', 'Code'] 
                               and not col.startswith('Unnamed')
                               and col.strip().isdigit()]
                
                # Process each country
                for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing countries"):
                    if pd.notna(row.get('Country Name')):
                        text = self._create_wbi_text(row, indicator_name, year_columns)
                        
                        metadata = {
                            "source": "WBI",
                            "source_file": csv_file.name,
                            "country": row.get('Country Name', 'Unknown'),
                            "country_code": row.get('Code', ''),
                            "indicator": indicator_name,
                        }
                        all_texts.append(text)
                        all_metadata.append(metadata)
                
            except Exception as e:
                console.print(f"[red]Error processing {csv_file.name}: {e}[/red]")
        
        if all_texts:
            console.print(f"[cyan]Adding {len(all_texts)} WBI documents to vector store...[/cyan]")
            self.add_documents(all_texts, all_metadata)
            self.save_index()
        else:
            console.print("[yellow]No documents to add from WBI[/yellow]")
    
    def _create_wbi_text(self, row: pd.Series, indicator_name: str, year_columns: List[str]) -> str:
        """Create searchable text from WBI row."""
        parts = []
        
        country_name = row.get('Country Name', 'Unknown')
        country_code = row.get('Code', '')
        
        parts.append(f"Country: {country_name} ({country_code})")
        parts.append(f"Indicator: {indicator_name}")
        
        # Focus on recent years (last 20 years with data)
        recent_data = []
        for year in reversed(year_columns):
            value = row.get(year)
            if pd.notna(value) and value != '':
                try:
                    # Format number for readability
                    num_value = float(value)
                    if abs(num_value) >= 1e9:
                        formatted = f"{num_value/1e9:.2f}B"
                    elif abs(num_value) >= 1e6:
                        formatted = f"{num_value/1e6:.2f}M"
                    elif abs(num_value) >= 1000:
                        formatted = f"{num_value/1000:.2f}K"
                    else:
                        formatted = f"{num_value:.2f}"
                    recent_data.append(f"{year}: {formatted}")
                except (ValueError, TypeError):
                    recent_data.append(f"{year}: {value}")
                
                if len(recent_data) >= 20:  # Limit to recent 20 data points
                    break
        
        if recent_data:
            parts.append(f"Recent values: {', '.join(reversed(recent_data))}")
        else:
            parts.append("No recent data available")
        
        # Calculate trend if we have enough data points
        if len(recent_data) >= 3:
            try:
                values = []
                for item in recent_data[:3]:
                    val_str = item.split(': ')[1]
                    # Remove B/M/K suffixes and convert back
                    if val_str.endswith('B'):
                        values.append(float(val_str[:-1]) * 1e9)
                    elif val_str.endswith('M'):
                        values.append(float(val_str[:-1]) * 1e6)
                    elif val_str.endswith('K'):
                        values.append(float(val_str[:-1]) * 1000)
                    else:
                        values.append(float(val_str))
                
                if len(values) >= 2:
                    if values[0] > values[-1]:
                        trend = "declining"
                    elif values[0] < values[-1]:
                        trend = "increasing"
                    else:
                        trend = "stable"
                    parts.append(f"Trend: {trend}")
            except (ValueError, IndexError, TypeError):
                pass
        
        return " | ".join(parts)
    
    def ingest_imf_data(self, imf_path: Optional[str] = None):
        """Ingest IMF World Economic Outlook data into the vector store."""
        if imf_path is None:
            imf_path = "historical_context/IMF"
        
        imf_dir = Path(imf_path)
        if not imf_dir.exists():
            console.print(f"[yellow]IMF directory not found: {imf_path}[/yellow]")
            console.print("[yellow]Please place IMF Excel/XLS files in historical_context/IMF/[/yellow]")
            return
        
        # Look for Excel files
        excel_files = list(imf_dir.glob("*.xlsx")) + list(imf_dir.glob("*.xls"))
        if not excel_files:
            console.print(f"[yellow]No Excel files found in {imf_path}[/yellow]")
            return
        
        console.print(f"[cyan]Found {len(excel_files)} IMF Excel file(s)[/cyan]")
        
        all_texts = []
        all_metadata = []
        
        for excel_file in excel_files:
            console.print(f"[cyan]Processing {excel_file.name}...[/cyan]")
            
            try:
                # Read the data - IMF WEO files are typically tab-separated
                # Try different approaches based on file extension and encoding
                try:
                    if excel_file.suffix.lower() == '.xlsx':
                        # True Excel format
                        df = pd.read_excel(excel_file, header=0, engine='openpyxl')
                    elif excel_file.suffix.lower() == '.xls':
                        # Try reading as tab-separated text file with different encodings
                        # Many .xls files from IMF are actually tab-delimited text files (often UTF-16LE encoded)
                        try:
                            df = pd.read_csv(excel_file, sep='\t', encoding='utf-16le', low_memory=False)
                        except UnicodeDecodeError:
                            try:
                                df = pd.read_csv(excel_file, sep='\t', encoding='utf-16', low_memory=False)
                            except UnicodeDecodeError:
                                try:
                                    df = pd.read_csv(excel_file, sep='\t', encoding='utf-8', low_memory=False)
                                except UnicodeDecodeError:
                                    try:
                                        df = pd.read_csv(excel_file, sep='\t', encoding='latin-1', low_memory=False)
                                    except:
                                        df = pd.read_csv(excel_file, sep='\t', encoding='iso-8859-1', low_memory=False)
                    else:
                        df = pd.read_excel(excel_file, header=0)
                except Exception as e:
                    console.print(f"[yellow]Could not read as Excel, trying as tab-separated CSV: {e}[/yellow]")
                    # Final fallback: try as tab-separated with different encodings
                    try:
                        df = pd.read_csv(excel_file, sep='\t', encoding='latin-1', low_memory=False)
                    except:
                        df = pd.read_csv(excel_file, sep='\t', encoding='iso-8859-1', low_memory=False)
                
                console.print(f"  Loaded {len(df)} records")
                
                # Get year columns (columns that are numeric representing years)
                all_columns = df.columns.tolist()
                # IMF files typically have year columns from position 9 onwards
                # The last column is "Estimates Start After"
                year_columns = []
                for col in all_columns:
                    try:
                        # Try to parse as year (handle both int and string columns)
                        col_str = str(col).strip()
                        year = int(col_str)
                        if 1900 <= year <= 2100:  # Valid year range
                            year_columns.append(col)
                    except (ValueError, TypeError):
                        continue
                
                console.print(f"  Found {len(year_columns)} year columns from {year_columns[0] if year_columns else 'N/A'} to {year_columns[-1] if year_columns else 'N/A'}")
                
                # Process each row (each row is a country + indicator combination)
                for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing indicators"):
                    if pd.notna(row.get('Country')):
                        text = self._create_imf_text(row, year_columns)
                        
                        metadata = {
                            "source": "IMF",
                            "source_file": excel_file.name,
                            "country": row.get('Country', 'Unknown'),
                            "iso_code": row.get('ISO', ''),
                            "weo_subject_code": row.get('WEO Subject Code', ''),
                            "subject_descriptor": row.get('Subject Descriptor', ''),
                            "units": row.get('Units', ''),
                        }
                        all_texts.append(text)
                        all_metadata.append(metadata)
                
            except Exception as e:
                console.print(f"[red]Error processing {excel_file.name}: {e}[/red]")
                import traceback
                traceback.print_exc()
        
        if all_texts:
            console.print(f"[cyan]Adding {len(all_texts)} IMF documents to vector store...[/cyan]")
            self.add_documents(all_texts, all_metadata)
            self.save_index()
        else:
            console.print("[yellow]No documents to add from IMF[/yellow]")
    
    def _create_imf_text(self, row: pd.Series, year_columns: List[str]) -> str:
        """Create searchable text from IMF row."""
        parts = []
        
        # Basic information
        country = row.get('Country', 'Unknown')
        subject_descriptor = row.get('Subject Descriptor', '')
        units = row.get('Units', '')
        scale = row.get('Scale', '')
        
        parts.append(f"Country: {country}")
        parts.append(f"Indicator: {subject_descriptor}")
        
        if units:
            unit_text = f"{units}"
            if scale and scale != 'Units':
                unit_text += f" ({scale})"
            parts.append(f"Units: {unit_text}")
        
        # Focus on recent years (last 15 years with data)
        recent_data = []
        for year in reversed(year_columns[-20:]):  # Look at last 20 years
            value = row.get(year)
            if pd.notna(value) and value != '' and str(value).lower() != 'n/a':
                try:
                    # Format number for readability
                    value_str = str(value).replace(',', '')  # Remove comma separators
                    num_value = float(value_str)
                    
                    # Format based on scale
                    if scale == 'Billions':
                        formatted = f"{num_value:.2f}B"
                    elif scale == 'Millions':
                        formatted = f"{num_value:.2f}M"
                    elif 'Percent' in str(units):
                        formatted = f"{num_value:.2f}%"
                    else:
                        # Auto-format large numbers
                        if abs(num_value) >= 1000:
                            formatted = f"{num_value:,.2f}"
                        else:
                            formatted = f"{num_value:.2f}"
                    
                    recent_data.append(f"{year}: {formatted}")
                except (ValueError, TypeError):
                    # Keep non-numeric values as-is
                    recent_data.append(f"{year}: {value}")
                
                if len(recent_data) >= 15:  # Limit to recent 15 data points
                    break
        
        if recent_data:
            parts.append(f"Recent values: {', '.join(reversed(recent_data))}")
        else:
            parts.append("No recent data available")
        
        # Calculate trend if we have enough data points
        if len(recent_data) >= 3:
            try:
                values = []
                for item in recent_data[:3]:
                    val_str = item.split(': ')[1]
                    # Remove formatting characters and convert
                    val_str = val_str.replace(',', '').replace('B', '').replace('M', '').replace('%', '')
                    values.append(float(val_str))
                
                if len(values) >= 2:
                    # Compare most recent to oldest in our sample
                    change_pct = ((values[0] - values[-1]) / abs(values[-1])) * 100 if values[-1] != 0 else 0
                    if change_pct > 5:
                        trend = f"increasing (↑{change_pct:.1f}%)"
                    elif change_pct < -5:
                        trend = f"declining (↓{abs(change_pct):.1f}%)"
                    else:
                        trend = "stable"
                    parts.append(f"Trend: {trend}")
            except (ValueError, IndexError, TypeError, ZeroDivisionError):
                pass
        
        # Add subject notes if they contain useful context (but truncate long notes)
        subject_notes = row.get('Subject Notes', '')
        if subject_notes and pd.notna(subject_notes):
            notes_str = str(subject_notes)[:300]  # Limit length
            if len(notes_str) > 0:
                parts.append(f"Description: {notes_str}")
        
        return " | ".join(parts)
    
    def ingest_freedom_world_data(self, freedom_world_path: Optional[str] = None):
        """Ingest Freedom in the World data into the vector store."""
        if freedom_world_path is None:
            freedom_world_path = "historical_context/FREEDOM_WORLD"
        
        freedom_world_dir = Path(freedom_world_path)
        if not freedom_world_dir.exists():
            console.print(f"[yellow]FREEDOM_WORLD directory not found: {freedom_world_path}[/yellow]")
            console.print("[yellow]Please place Freedom in the World Excel files in historical_context/FREEDOM_WORLD/[/yellow]")
            return
        
        # Look for the main Excel file
        excel_files = list(freedom_world_dir.glob("*.xlsx")) + list(freedom_world_dir.glob("*.xls"))
        if not excel_files:
            console.print(f"[yellow]No Excel files found in {freedom_world_path}[/yellow]")
            return
        
        console.print(f"[cyan]Found {len(excel_files)} Freedom in the World Excel file(s)[/cyan]")
        
        all_texts = []
        all_metadata = []
        
        for excel_file in excel_files:
            console.print(f"[cyan]Processing {excel_file.name}...[/cyan]")
            
            try:
                # Read the data sheet (FIW13-25 or similar)
                # First, detect available sheets
                xl_file = pd.ExcelFile(excel_file)
                data_sheet = None
                
                # Look for data sheet (typically named FIW13-25 or similar)
                for sheet_name in xl_file.sheet_names:
                    if sheet_name != 'Index' and ('FIW' in sheet_name or 'data' in sheet_name.lower()):
                        data_sheet = sheet_name
                        break
                
                if not data_sheet:
                    console.print(f"[yellow]Could not find data sheet in {excel_file.name}, skipping[/yellow]")
                    continue
                
                console.print(f"  Reading sheet: {data_sheet}")
                df = pd.read_excel(excel_file, sheet_name=data_sheet, header=0)
                
                # Clean up the DataFrame - first row contains proper headers
                # Set proper column names from the first row if needed
                if 'Country/Territory' not in df.columns:
                    df.columns = df.iloc[0]
                    df = df[1:].reset_index(drop=True)
                
                console.print(f"  Loaded {len(df)} records")
                
                # Process each row (each row is a country/territory for a specific year)
                for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
                    if pd.notna(row.get('Country/Territory')):
                        text = self._create_freedom_world_text(row)
                        
                        metadata = {
                            "source": "FREEDOM_WORLD",
                            "source_file": excel_file.name,
                            "country": row.get('Country/Territory', 'Unknown'),
                            "region": row.get('Region', ''),
                            "edition": str(row.get('Edition', '')),
                            "status": row.get('Status', ''),
                            "pr_rating": str(row.get('PR rating', '')),
                            "cl_rating": str(row.get('CL rating', '')),
                        }
                        all_texts.append(text)
                        all_metadata.append(metadata)
                
            except Exception as e:
                console.print(f"[red]Error processing {excel_file.name}: {e}[/red]")
                import traceback
                traceback.print_exc()
        
        if all_texts:
            console.print(f"[cyan]Adding {len(all_texts)} Freedom in the World documents to vector store...[/cyan]")
            self.add_documents(all_texts, all_metadata)
            self.save_index()
        else:
            console.print("[yellow]No documents to add from FREEDOM_WORLD[/yellow]")
    
    def _create_freedom_world_text(self, row: pd.Series) -> str:
        """Create searchable text from Freedom in the World row."""
        parts = []
        
        # Basic information
        country = row.get('Country/Territory', 'Unknown')
        region = row.get('Region', '')
        edition = row.get('Edition', '')
        c_or_t = row.get('C/T', '')
        
        parts.append(f"Country: {country}")
        if region:
            parts.append(f"Region: {region}")
        parts.append(f"Year: {edition}")
        
        # Type (country or territory)
        if c_or_t == 'c':
            parts.append("Type: Country")
        elif c_or_t == 't':
            parts.append("Type: Territory")
        
        # Freedom status
        status = row.get('Status', '')
        if status == 'F':
            parts.append("Status: Free")
        elif status == 'PF':
            parts.append("Status: Partly Free")
        elif status == 'NF':
            parts.append("Status: Not Free")
        
        # Main ratings
        pr_rating = row.get('PR rating')
        cl_rating = row.get('CL rating')
        if pd.notna(pr_rating):
            parts.append(f"Political Rights Rating: {pr_rating}/7")
        if pd.notna(cl_rating):
            parts.append(f"Civil Liberties Rating: {cl_rating}/7")
        
        # Aggregate scores
        score_fields = [
            ('A', 'Electoral Process'),
            ('B', 'Political Pluralism and Participation'),
            ('C', 'Functioning of Government'),
            ('PR', 'Political Rights Total'),
            ('D', 'Freedom of Expression and Belief'),
            ('E', 'Associational and Organizational Rights'),
            ('F', 'Rule of Law'),
            ('G', 'Personal Autonomy and Individual Rights'),
            ('CL', 'Civil Liberties Total'),
            ('Total', 'Overall Freedom Score'),
        ]
        
        for field, label in score_fields:
            value = row.get(field)
            if pd.notna(value) and value != '':
                parts.append(f"{label}: {value}")
        
        # Detailed scores (subcategory components)
        detailed_fields = [
            ('A1', 'Electoral Framework'),
            ('A2', 'Electoral Process'),
            ('A3', 'Electoral Outcome'),
            ('B1', 'Political Parties'),
            ('B2', 'Opposition'),
            ('B3', 'Political Choice'),
            ('B4', 'Minority Participation'),
            ('C1', 'Government Function'),
            ('C2', 'Corruption'),
            ('C3', 'Transparency'),
            ('D1', 'Free Media'),
            ('D2', 'Free Expression'),
            ('D3', 'Academic Freedom'),
            ('D4', 'Religious Freedom'),
            ('E1', 'Assembly Rights'),
            ('E2', 'NGO Rights'),
            ('E3', 'Labor Rights'),
            ('F1', 'Independent Judiciary'),
            ('F2', 'Due Process'),
            ('F3', 'Protection from Violence'),
            ('F4', 'Equal Treatment'),
            ('G1', 'Freedom of Movement'),
            ('G2', 'Property Rights'),
            ('G3', 'Social Freedoms'),
            ('G4', 'Equality of Opportunity'),
        ]
        
        # Include detailed scores to provide more context
        detailed_parts = []
        for field, label in detailed_fields:
            value = row.get(field)
            if pd.notna(value) and value != '' and str(value) != 'N/A':
                detailed_parts.append(f"{label}: {value}")
        
        if detailed_parts:
            parts.append(f"Detailed scores: {', '.join(detailed_parts)}")
        
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


def query_faiss(query: str, source: Optional[str] = None, top_k: int = 5) -> str:
    """
    Query the FAISS vector store with optional source filtering.
    
    Args:
        query: The search query
        source: Optional source filter ("ACLED", "CIA_FACTS", "WBI", "FREEDOM_WORLD", or "IMF")
        top_k: Number of top results to return
        
    Returns:
        Formatted context string with search results
    """
    store = VectorStore()
    
    # Get more results initially if we need to filter
    search_k = top_k * 3 if source else top_k
    results = store.search(query, top_k=search_k)
    
    # Filter by source if specified
    if source:
        results = [r for r in results if r['metadata'].get('source') == source]
        results = results[:top_k]  # Trim to requested top_k
    
    # Format results into context string
    context_parts = []
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        doc = result['document']
        score = result['score']
        
        source_name = metadata.get('source', 'Unknown')
        country = metadata.get('country', 'N/A')
        
        context_parts.append(f"[{i}] Source: {source_name} | Country: {country} | Relevance: {score:.3f}")
        context_parts.append(f"    {doc[:500]}...")  # Truncate long documents
        context_parts.append("")
    
    return "\n".join(context_parts) if context_parts else "No relevant context found."


def main():
    """CLI for vector store management."""
    parser = argparse.ArgumentParser(description="HAWK-AI Vector Store Manager")
    parser.add_argument('--rebuild', action='store_true', help='Rebuild index from all data sources')
    parser.add_argument('--ingest-acled', action='store_true', help='Ingest ACLED data only')
    parser.add_argument('--ingest-cia-facts', action='store_true', help='Ingest CIA World Factbook data only')
    parser.add_argument('--ingest-wbi', action='store_true', help='Ingest World Bank Indicators data only')
    parser.add_argument('--ingest-freedom-world', action='store_true', help='Ingest Freedom in the World data only')
    parser.add_argument('--ingest-imf', action='store_true', help='Ingest IMF World Economic Outlook data only')
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
        console.print("\n[bold cyan]Ingesting World Bank Indicators data...[/bold cyan]")
        store.ingest_wbi_data()
        console.print("\n[bold cyan]Ingesting Freedom in the World data...[/bold cyan]")
        store.ingest_freedom_world_data()
        console.print("\n[bold cyan]Ingesting IMF World Economic Outlook data...[/bold cyan]")
        store.ingest_imf_data()
        console.print("\n[bold green]✓ Rebuild complete![/bold green]")
    
    if args.ingest_acled:
        console.print("[yellow]Ingesting ACLED data...[/yellow]")
        store.ingest_acled_data()
    
    if args.ingest_cia_facts:
        console.print("[yellow]Ingesting CIA World Factbook data...[/yellow]")
        store.ingest_cia_facts_data()
    
    if args.ingest_wbi:
        console.print("[yellow]Ingesting World Bank Indicators data...[/yellow]")
        store.ingest_wbi_data()
    
    if args.ingest_freedom_world:
        console.print("[yellow]Ingesting Freedom in the World data...[/yellow]")
        store.ingest_freedom_world_data()
    
    if args.ingest_imf:
        console.print("[yellow]Ingesting IMF World Economic Outlook data...[/yellow]")
        store.ingest_imf_data()
    
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
