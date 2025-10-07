import yt_dlp
from shazamio import Shazam
import asyncio
import tempfile
import os
from pydub import AudioSegment
from pathlib import Path
import uuid
import json
from datetime import datetime


def download_audio(url, output_path):
    output_template = str(output_path)
    
    opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False
    }
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"  Title: {info.get('title', 'Unknown')}")
            print(f"  Duration: {info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}")
            
            ydl.download([url])
        
        final_path = output_template + '.mp3'
        
        if not os.path.exists(final_path):
            raise FileNotFoundError(f"Downloaded file not found at {final_path}")
        
        return final_path
        
    except Exception as e:
        raise Exception(f"Failed to download audio: {str(e)}")


async def identify_song(audio_chunk):
    shazam = Shazam()
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
            audio_chunk.export(temp_path, format='mp3')
        
        result = await shazam.recognize(temp_path)
        
        os.unlink(temp_path)
        
        if result and 'track' in result:
            track = result['track']
            return {
                'title': track.get('title', 'Unknown'),
                'artist': track.get('subtitle', 'Unknown Artist'),
                'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown Album') 
                         if track.get('sections') else 'Unknown Album',
                'shazam_url': track.get('url', ''),
                'key': track.get('key', ''),
                'raw': result
            }
        
        return None
        
    except Exception as e:
        print(f"Error identifying: {str(e)}")
        return None


def split_audio(audio_path, interval_ms=30000, sample_length_ms=15000):
    audio = AudioSegment.from_mp3(audio_path)
    chunks = []
    
    # Sample every interval_ms, taking sample_length_ms clips
    for timestamp in range(0, len(audio), interval_ms):
        end = min(timestamp + sample_length_ms, len(audio))
        chunk = audio[timestamp:end]
        
        # Only include if chunk is long enough (at least 10 seconds)
        if len(chunk) >= 10000:
            chunks.append((timestamp, chunk))
    
    return chunks


def format_timestamp(ms):
    """Convert milliseconds to MM:SS format"""
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def deduplicate_songs(song_results):
    if not song_results:
        return []
    
    unique = []
    last_song = None
    
    for result in song_results:
        song_id = result['result'].get('key')
        
        if song_id != last_song:
            unique.append(result)
            last_song = song_id
    
    return unique


def export_results(songs, source_url):
    """Export results to JSON file"""
    output = {
        'source': source_url,
        'processed_at': datetime.now().isoformat(),
        'total_songs': len(songs),
        'songs': songs
    }
    
    filename = f"song_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"  Saved to: {filename}")


async def main():
    youtube_url = input("Enter the YouTube URL: ")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"{uuid.uuid4()}"
        
        try:
            # Step 1: Download
            print("[1/4] Downloading audio...")
            file_path = download_audio(youtube_url, str(audio_path))
            print(f"\n✓ Downloaded to: {file_path}")
            
            # Step 2: Split audio
            print("\n[2/4] Splitting audio into chunks...")
            audio_chunks = split_audio(file_path)
            print(f"✓ Created {len(audio_chunks)} chunks")
            
            # Step 3: Identify songs
            print(f"\n[3/4] Identifying songs from {len(audio_chunks)} chunks...")
            song_results = []
            
            for index, (timestamp_ms, chunk) in enumerate(audio_chunks):
                timestamp_str = format_timestamp(timestamp_ms)
                print(f"  → Chunk {index + 1}/{len(audio_chunks)} at {timestamp_str}...", end=" ")
                
                song_result = await identify_song(chunk)
                
                if song_result:
                    print(f"✓ {song_result.get('title')} - {song_result.get('artist')}")
                    song_results.append({
                        'timestamp': timestamp_ms,
                        'timestamp_formatted': timestamp_str,
                        'result': song_result
                    })
                else:
                    print("✗ Not identified")
                
                # Rate limiting - be nice to the API
                await asyncio.sleep(1)
            
            # Step 4: Deduplicate and export
            print(f"\n[4/4] Processing results...")
            unique_songs = deduplicate_songs(song_results)
            print(f"✓ Found {len(unique_songs)} unique songs\n")
            
            # Print summary
            print("=" * 60)
            print("IDENTIFIED SONGS:")
            print("=" * 60)
            for i, song in enumerate(unique_songs, 1):
                result = song['result']
                print(f"{i}. [{song['timestamp_formatted']}] {result['title']} - {result['artist']}")
            print("=" * 60)

            return unique_songs
        except Exception as e:
            print(f"\n✗ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())