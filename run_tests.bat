@echo off
chcp 65001 > nul
title Bộ Kiểm Thử Tự Động Selenium - Swag Labs
cls

echo ===============================================================================
echo                BỘ KIỂM THỬ TỰ ĐỘNG SELENIUM (PYTHON + EDGE)
echo ===============================================================================
echo 1. Chạy kiểm thử có giao diện trình duyệt (Headed - Xem trực tiếp tự động hoá)
echo 2. Chạy kiểm thử chế độ chạy ngầm (Headless - Nhanh, không hiện cửa sổ)
echo 3. Mở thư mục ảnh chụp màn hình (screenshots)
echo 4. Thoát
echo ===============================================================================

set /p choice="Nhập lựa chọn của bạn (1-4, mặc định 1): "
if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo.
    echo Đang khởi chạy Selenium ở chế độ có giao diện...
    python test_suite.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Đang khởi chạy Selenium ở chế độ chạy ngầm (Headless)...
    python test_suite.py --headless
    goto end
)

if "%choice%"=="3" (
    explorer screenshots
    exit /b
)

if "%choice%"=="4" (
    exit /b
)

echo Lựa chọn không hợp lệ.

:end
echo.
echo Nhấn phím bất kỳ để thoát...
pause > nul
