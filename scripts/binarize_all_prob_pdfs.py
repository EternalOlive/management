# -*- coding: utf-8 -*-
import os
import glob
import fitz  # PyMuPDF
import cv2
import numpy as np

def binarize_page_img(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # Bilateral filter for edge-preserving noise reduction
    bilateral = cv2.bilateralFilter(gray, 5, 50, 50)
    # Adaptive thresholding: pure white background, crisp solid black text
    binarized = cv2.adaptiveThreshold(
        bilateral, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 15
    )
    return binarized

def binarize_pdf(pdf_path, out_path, dpi=200):
    print(f"\nProcessing {pdf_path} -> {out_path} ...")
    src_doc = fitz.open(pdf_path)
    dst_doc = fitz.open()

    total = len(src_doc)
    for idx in range(total):
        page = src_doc[idx]
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # Apply high-precision adaptive binarization
        bin_img = binarize_page_img(img_bgr)

        # Encode to compressed 1-channel PNG
        success, enc = cv2.imencode('.png', bin_img, [cv2.IMWRITE_PNG_COMPRESSION, 6])
        if not success:
            raise RuntimeError(f"Failed to encode page {idx}")

        img_bytes = enc.tobytes()

        # Create new page in dst_doc with original dimensions
        new_page = dst_doc.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=img_bytes)

        if (idx + 1) % 10 == 0 or idx + 1 == total:
            print(f"  Page {idx + 1} / {total} done")

    # Save with maximum compression and garbage collection
    dst_doc.save(out_path, garbage=4, deflate=True)
    dst_doc.close()
    src_doc.close()

    orig_sz = os.path.getsize(pdf_path) / (1024 * 1024)
    new_sz = os.path.getsize(out_path) / (1024 * 1024)
    print(f"Completed {os.path.basename(out_path)}: {orig_sz:.2f} MB -> {new_sz:.2f} MB")

def main():
    pdf_dir = 'pdf'
    prob_files = sorted(glob.glob(os.path.join(pdf_dir, 'prob_0*.pdf')))
    print(f"Found {len(prob_files)} problem PDF files.")

    for p in prob_files:
        base = os.path.basename(p)
        out_p = os.path.join(pdf_dir, 'bin_' + base)
        binarize_pdf(p, out_p, dpi=200)

    print("\nAll PDFs binarized successfully into bin_prob_*.pdf!")

if __name__ == '__main__':
    main()
