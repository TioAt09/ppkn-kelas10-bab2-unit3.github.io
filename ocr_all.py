import asyncio
import winsdk.windows.media.ocr as ocr
import winsdk.windows.storage.streams as streams
import winsdk.windows.graphics.imaging as imaging
import pypdf
import os

async def ocr_page(page_idx, page):
    # Find the largest image (main page content)
    if not page.images:
        return ""
    large_img = max(page.images, key=lambda x: len(x.data))
    
    # Create InMemoryRandomAccessStream
    stream = streams.InMemoryRandomAccessStream()
    writer = streams.DataWriter(stream)
    writer.write_bytes(large_img.data)
    await writer.store_async()
    await writer.flush_async()
    stream.seek(0)
    
    # Decode image
    decoder = await imaging.BitmapDecoder.create_async(stream)
    software_bitmap = await decoder.get_software_bitmap_async()
    
    # Create OCR engine (use user profile or default)
    engine = ocr.OcrEngine.try_create_from_user_profile_languages()
    if not engine:
        langs = ocr.OcrEngine.get_available_recognizer_languages()
        engine = ocr.OcrEngine.try_create_from_language(langs[0])
        
    result = await engine.recognize_async(software_bitmap)
    return result.text

async def main():
    print("Reading KELAS 10_BAB 2_UNIT 3_PPKN.pdf...")
    reader = pypdf.PdfReader('PPKN_BAB 2_UNIT 3_KELAS 10.pdf')
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")
    
    with open('extracted_text_ocr.txt', 'w', encoding='utf-8') as f:
        for idx in range(total_pages):
            print(f"Processing Page {idx+1}/{total_pages}...")
            try:
                page_text = await ocr_page(idx, reader.pages[idx])
                f.write(f"=== PAGE {idx+1} ===\n")
                f.write(page_text)
                f.write("\n\n")
            except Exception as e:
                print(f"Error processing Page {idx+1}: {e}")
                f.write(f"=== PAGE {idx+1} ERROR: {e} ===\n\n")
                
    print("OCR extraction completed and saved to extracted_text_ocr.txt!")

asyncio.run(main())
