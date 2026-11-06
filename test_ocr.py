import asyncio
import winsdk.windows.media.ocr as ocr
import winsdk.windows.storage.streams as streams
import winsdk.windows.graphics.imaging as imaging
import pypdf
import io

async def test_ocr():
    reader = pypdf.PdfReader('PPKN_BAB 2_UNIT 3_KELAS 10.pdf')
    # Get first page
    page = reader.pages[0]
    # Find the largest image
    large_img = max(page.images, key=lambda x: len(x.data))
    print(f"Testing OCR on largest image: {large_img.name} ({len(large_img.data)} bytes)")
    
    # Create InMemoryRandomAccessStream
    stream = streams.InMemoryRandomAccessStream()
    writer = streams.DataWriter(stream)
    writer.write_bytes(large_img.data)
    await writer.store_async()
    await writer.flush_async()
    stream.seek(0)
    
    # Load decoder and get software bitmap
    decoder = await imaging.BitmapDecoder.create_async(stream)
    software_bitmap = await decoder.get_software_bitmap_async()
    
    # Create OCR engine
    engine = ocr.OcrEngine.try_create_from_user_profile_languages()
    if not engine:
        raise Exception("Could not create OCR engine")
    
    print(f"Using OCR Engine language: {engine.recognizer_language.language_tag}")
    
    result = await engine.recognize_async(software_bitmap)
    print("\n--- OCR RESULT ---")
    print(result.text)
    print("------------------")

asyncio.run(test_ocr())
