"""
Embeddings cache system for efficient document processing
Caches embeddings and chunks to avoid recomputation for the same content
"""

import hashlib
import pickle
import os
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger("uvicorn")

class EmbeddingsCache:
    """Cache system for document embeddings and chunks"""

    def __init__(self, cache_dir: str = "./embeddings_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        logger.info(f"Embeddings cache initialized at: {self.cache_dir}")

    def _get_content_hash(self, content: str) -> str:
        """Generate MD5 hash of content for cache key"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _get_cache_file(self, content_hash: str) -> Path:
        """Get cache file path for content hash"""
        return self.cache_dir / f"embeddings_{content_hash}.pkl"

    def _get_metadata_file(self, content_hash: str) -> Path:
        """Get metadata file path for content hash"""
        return self.cache_dir / f"metadata_{content_hash}.json"

    def get_cached_embeddings(self, content: str, chunk_size: int = 1000) -> Optional[Dict[str, Any]]:
        """Retrieve cached embeddings if they exist and match parameters"""
        content_hash = self._get_content_hash(content)
        cache_file = self._get_cache_file(content_hash)
        metadata_file = self._get_metadata_file(content_hash)

        if cache_file.exists() and metadata_file.exists():
            try:
                # Load metadata first
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Verify chunk_size matches
                if metadata.get('chunk_size') != chunk_size:
                    logger.info(f"Cache miss - chunk size mismatch: {metadata.get('chunk_size')} vs {chunk_size}")
                    return None

                # Load cached embeddings
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)

                logger.info(f"Cache hit for content hash: {content_hash[:8]}... ({len(cached_data['chunks'])} chunks)")
                return cached_data

            except Exception as e:
                logger.warning(f"Failed to load cache for {content_hash[:8]}...: {e}")
                # Clean up corrupted cache files
                try:
                    cache_file.unlink(missing_ok=True)
                    metadata_file.unlink(missing_ok=True)
                except:
                    pass

        logger.info(f"Cache miss for content hash: {content_hash[:8]}...")
        return None

    def cache_embeddings(self, content: str, chunks: List[str], embeddings: List[List[float]], chunk_size: int = 1000):
        """Cache embeddings and chunks for future use"""
        content_hash = self._get_content_hash(content)
        cache_file = self._get_cache_file(content_hash)
        metadata_file = self._get_metadata_file(content_hash)

        # Prepare cache data
        cache_data = {
            'content_hash': content_hash,
            'chunks': chunks,
            'embeddings': embeddings,
            'chunk_count': len(chunks)
        }

        # Prepare metadata
        metadata = {
            'content_hash': content_hash,
            'chunk_size': chunk_size,
            'chunk_count': len(chunks),
            'content_length': len(content),
            'created_at': datetime.now().isoformat(),
            'cache_version': '1.0'
        }

        try:
            # Save embeddings data
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)

            # Save metadata
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Cached {len(chunks)} chunks and embeddings for hash: {content_hash[:8]}...")

        except Exception as e:
            logger.error(f"Failed to cache embeddings: {e}")
            # Clean up partial files
            try:
                cache_file.unlink(missing_ok=True)
                metadata_file.unlink(missing_ok=True)
            except:
                pass

    def clear_cache(self):
        """Clear all cached embeddings"""
        try:
            for file in self.cache_dir.glob("embeddings_*.pkl"):
                file.unlink()
            for file in self.cache_dir.glob("metadata_*.json"):
                file.unlink()
            logger.info("Embeddings cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache"""
        try:
            cache_files = list(self.cache_dir.glob("embeddings_*.pkl"))
            metadata_files = list(self.cache_dir.glob("metadata_*.json"))

            total_size = sum(f.stat().st_size for f in cache_files)

            # Load some metadata for detailed stats
            total_chunks = 0
            oldest_date = None
            newest_date = None

            for metadata_file in metadata_files:
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)

                    total_chunks += metadata.get('chunk_count', 0)

                    created_at = datetime.fromisoformat(metadata.get('created_at', ''))
                    if oldest_date is None or created_at < oldest_date:
                        oldest_date = created_at
                    if newest_date is None or created_at > newest_date:
                        newest_date = created_at

                except Exception:
                    continue

            return {
                'cache_entries': len(cache_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_chunks': total_chunks,
                'oldest_entry': oldest_date.isoformat() if oldest_date else None,
                'newest_entry': newest_date.isoformat() if newest_date else None,
                'cache_directory': str(self.cache_dir)
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'error': str(e)}