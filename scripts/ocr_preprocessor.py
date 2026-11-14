# -*- coding: utf-8 -*-
"""
OCR Preprocessor Module
- PDF 페이지 및 스캔 이미지를 위한 고성능 전처리 파이프라인
1. 선명한 300 DPI 렌더링
2. 그레이스케일 및 대비 강화(CLAHE)
3. 노이즈 제거 및 적응형 이진화(Adaptive Gaussian Thresholding)
4. 자동 기울기 보정(Deskew)
"""

import os
import cv2
import numpy as np
import fitz # PyMuPDF

def binarize_image(img_cv, block_size=25, c_val=12):
    """
    적응형 가우시안 이진화(Adaptive Gaussian Thresholding):
    - 그림자, 누런 배경, 뒷면 비침(Bleed-through)을 깨끗이 날리고
    - 글자 획(Stroke)만 선명한 흑백으로 분리
    """
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv

    # 노이즈 살짝 부드럽게 (가우시안 필터)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # 적응형 이진화 (배경 흰색 255, 글자 검은색 0)
    binarized = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size, c_val
    )
    return binarized

def deskew_image(img_cv):
    """
    기울기 보정(Deskew):
    - 문서의 수평선/텍스트 라인 기울기를 감지하여 정자세로 회전
    """
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv

    # 반전 (글자가 255, 배경이 0)
    thresh = cv2.bitwise_not(img_cv if len(img_cv.shape) == 2 else gray)
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 10:
        return img_cv

    angle = cv2.minAreaRect(coords)[-1]
    # 각도 보정 (-45도 ~ 45도 범위)
    if angle < -45:
        angle = -(90 + angle)
    elif angle > 45:
        angle = 90 - angle
    else:
        angle = -angle

    # 미세한 기울기(-5 ~ +5도 이내)만 보정하여 왜곡 방지
    if abs(angle) > 5.0 or abs(angle) < 0.2:
        return img_cv

    (h, w) = img_cv.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img_cv, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def preprocess_pdf_page(pdf_path, page_idx, dpi=300):
    """
    PDF 페이지를 300 DPI로 렌더링 후 이진화 및 기울기 보정 적용
    """
    doc = fitz.open(pdf_path)
    if page_idx >= len(doc):
        raise ValueError(f"Page index {page_idx} out of range (max {len(doc)-1})")

    page = doc[page_idx]
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    # Convert pixmap to numpy/OpenCV format
    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # 1. 기울기 보정
    deskewed = deskew_image(img_bgr)
    # 2. 적응형 이진화
    binarized = binarize_image(deskewed)

    return binarized

def test_preprocess_sample():
    pdf_path = os.path.join('pdf', 'prob_01.pdf')
    if os.path.exists(pdf_path):
        print(f"Testing preprocessing on {pdf_path} (page 0)...")
        res = preprocess_pdf_page(pdf_path, 0, dpi=200)
        out_path = 'preprocessed_sample_p1.png'
        cv2.imwrite(out_path, res)
        print(f"Preprocessed image successfully saved to: {out_path} ({res.shape[1]}x{res.shape[0]})")

if __name__ == '__main__':
    test_preprocess_sample()
