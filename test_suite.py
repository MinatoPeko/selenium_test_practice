"""
===============================================================================
BỘ KIỂM THỬ TỰ ĐỘNG BẰNG SELENIUM (SELENIUM TEST AUTOMATION SUITE)
Website mục tiêu: https://www.saucedemo.com/ (Swag Labs E-commerce Demo)
Trình duyệt: Microsoft Edge (tự động điều phối qua Selenium WebDriver)
===============================================================================
"""

import os
import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

BASE_URL = "https://www.saucedemo.com/"


class SauceDemoTestBase(unittest.TestCase):
    """Lớp cơ sở cấu hình WebDriver, timeouts và các helper functions."""

    driver = None
    wait = None

    @classmethod
    def setUpClass(cls):
        options = EdgeOptions()
        # Hỗ trợ cờ --headless qua dòng lệnh hoặc biến môi trường
        if "--headless" in sys.argv or os.environ.get("HEADLESS", "").lower() in ("true", "1"):
            options.add_argument("--headless=new")
        
        options.add_argument("--window-size=1366,768")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        cls.driver = webdriver.Edge(options=options)
        cls.driver.implicitly_wait(5)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()

    def setUp(self):
        """Trước mỗi test case, trở về trang chủ và dọn cookie, session/local storage."""
        self.driver.get(BASE_URL)
        self.driver.delete_all_cookies()
        try:
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        except Exception:
            pass

    def take_screenshot(self, name: str):
        """Chụp ảnh màn hình lưu vào thư mục screenshots/"""
        filepath = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
        self.driver.save_screenshot(filepath)
        return filepath

    def login_helper(self, username: str = "standard_user", password: str = "secret_sauce"):
        """Hàm dùng chung để đăng nhập nhanh vào hệ thống."""
        self.driver.get(BASE_URL)
        username_input = self.wait.until(EC.visibility_of_element_located((By.ID, "user-name")))
        password_input = self.driver.find_element(By.ID, "password")
        login_btn = self.driver.find_element(By.ID, "login-button")

        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        login_btn.click()

        if username == "standard_user":
            self.wait.until(EC.url_contains("/inventory.html"))


class TestSauceDemoSuite(SauceDemoTestBase):
    """Tập hợp 06 Test Case tự động hóa kiểm thử cho website Swag Labs."""

    def test_01_login_success(self):
        """
        TC01: Đăng nhập thành công với tài khoản hợp lệ.
        - Bước: Nhập standard_user / secret_sauce -> Bấm Login.
        - Kỳ vọng: Chuyển hướng tới inventory.html, hiển thị tiêu đề 'Products'.
        """
        print("\n[CHẠY] TC01: Đăng nhập thành công với tài khoản hợp lệ...")
        self.login_helper("standard_user", "secret_sauce")

        # Kiểm tra URL đã chuyển sang trang sản phẩm
        self.wait.until(EC.url_contains("/inventory.html"))
        current_url = self.driver.current_url
        self.assertIn("/inventory.html", current_url, "URL không đúng sau khi đăng nhập thành công!")

        # Kiểm tra tiêu đề trang
        title_el = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title")))
        self.assertEqual(title_el.text, "Products", "Tiêu đề trang sản phẩm không khớp!")

        self.take_screenshot("TC01_Login_Success")
        print("  -> PASS: Đăng nhập thành công, URL và tiêu đề chính xác.")

    def test_02_login_failed_locked_out(self):
        """
        TC02: Đăng nhập thất bại với tài khoản bị khóa.
        - Bước: Nhập locked_out_user / secret_sauce -> Bấm Login.
        - Kỳ vọng: Vẫn ở trang login, xuất hiện thông báo lỗi tài khoản bị khóa.
        """
        print("\n[CHẠY] TC02: Đăng nhập thất bại với tài khoản bị khóa...")
        self.login_helper("locked_out_user", "secret_sauce")

        # Chờ container thông báo lỗi xuất hiện
        error_el = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-test='error']"))
        )
        error_text = error_el.text
        expected_msg = "Epic sadface: Sorry, this user has been locked out."
        self.assertIn(expected_msg, error_text, f"Thông báo lỗi không đúng! Thực tế: {error_text}")

        self.take_screenshot("TC02_Login_Failed_LockedOut")
        print("  -> PASS: Đã bắt đúng thông báo lỗi tài khoản bị khóa.")

    def test_03_sort_products_price_low_to_high(self):
        """
        TC03: Sắp xếp / lọc danh sách sản phẩm theo giá tăng dần (Low to High).
        - Bước: Đăng nhập -> Chọn sắp xếp 'Price (low to high)' -> Lấy danh sách giá.
        - Kỳ vọng: Giá sản phẩm hiển thị theo thứ tự tăng dần từ thấp đến cao.
        """
        print("\n[CHẠY] TC03: Lọc & sắp xếp sản phẩm theo giá tăng dần...")
        self.login_helper("standard_user", "secret_sauce")
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "product_sort_container")))

        # Chọn option 'lohi'
        sort_dropdown = Select(self.driver.find_element(By.CLASS_NAME, "product_sort_container"))
        sort_dropdown.select_by_value("lohi")

        # Đợi danh sách giá cập nhật
        time.sleep(1)
        price_elements = self.driver.find_elements(By.CLASS_NAME, "inventory_item_price")
        prices = [float(el.text.replace("$", "").strip()) for el in price_elements]

        self.assertGreater(len(prices), 0, "Không tìm thấy sản phẩm nào trên trang!")
        self.assertEqual(prices, sorted(prices), f"Danh sách giá không được sắp xếp tăng dần! Thực tế: {prices}")

        self.take_screenshot("TC03_Sort_Price_LowToHigh")
        print(f"  -> PASS: Danh sách giá đã sắp xếp tăng dần: {prices}")

    def test_04_add_product_to_cart_and_verify(self):
        """
        TC04: Thêm sản phẩm vào giỏ hàng và kiểm tra giỏ hàng.
        - Bước: Đăng nhập -> Click 'Add to cart' tại sản phẩm 'Sauce Labs Backpack' -> Vào giỏ hàng.
        - Kỳ vọng: Badge giỏ hàng hiển thị '1', trong giỏ hàng có tên sản phẩm 'Sauce Labs Backpack'.
        """
        print("\n[CHẠY] TC04: Thêm sản phẩm vào giỏ hàng...")
        self.login_helper("standard_user", "secret_sauce")

        # Click nút Add to cart của sản phẩm đầu tiên (Sauce Labs Backpack)
        add_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-backpack"))
        )
        add_btn.click()

        # Kiểm tra badge hiển thị số 1
        badge = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge")))
        self.assertEqual(badge.text, "1", "Số lượng badge giỏ hàng không đúng!")

        # Bấm vào biểu tượng giỏ hàng
        cart_link = self.driver.find_element(By.CLASS_NAME, "shopping_cart_link")
        cart_link.click()

        # Kiểm tra URL và sản phẩm trong giỏ hàng
        self.wait.until(EC.url_contains("/cart.html"))
        item_name = self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "inventory_item_name"))
        ).text
        self.assertEqual(item_name, "Sauce Labs Backpack", "Tên sản phẩm trong giỏ không khớp!")

        self.take_screenshot("TC04_Add_To_Cart_Success")
        print("  -> PASS: Sản phẩm đã được thêm vào giỏ hàng chính xác.")

    def test_05_remove_product_from_cart(self):
        """
        TC05: Xóa sản phẩm khỏi giỏ hàng.
        - Bước: Đăng nhập -> Thêm sản phẩm -> Vào trang giỏ hàng -> Click 'Remove'.
        - Kỳ vọng: Sản phẩm bị xóa khỏi giỏ, badge giỏ hàng biến mất.
        """
        print("\n[CHẠY] TC05: Xóa sản phẩm khỏi giỏ hàng...")
        self.login_helper("standard_user", "secret_sauce")

        # Thêm sản phẩm và vào giỏ hàng
        add_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-backpack")))
        add_btn.click()
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.wait.until(EC.url_contains("/cart.html"))

        # Bấm nút Remove
        remove_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "remove-sauce-labs-backpack")))
        remove_btn.click()

        # Kiểm tra danh sách giỏ hàng không còn sản phẩm nào
        cart_items = self.driver.find_elements(By.CLASS_NAME, "cart_item")
        self.assertEqual(len(cart_items), 0, "Sản phẩm vẫn còn trong giỏ hàng sau khi nhấn Remove!")

        # Kiểm tra badge giỏ hàng không còn tồn tại
        badges = self.driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
        self.assertEqual(len(badges), 0, "Badge giỏ hàng vẫn còn hiển thị sau khi đã xóa hết hàng!")

        self.take_screenshot("TC05_Remove_From_Cart_Success")
        print("  -> PASS: Xóa sản phẩm thành công, giỏ hàng trống hoàn toàn.")

    def test_06_logout(self):
        """
        TC06: Đăng xuất khỏi hệ thống.
        - Bước: Đăng nhập -> Mở menu hamburger -> Click 'Logout'.
        - Kỳ vọng: Quay trở về trang chủ đăng nhập, nút Login hiển thị trở lại.
        """
        print("\n[CHẠY] TC06: Đăng xuất khỏi hệ thống...")
        self.login_helper("standard_user", "secret_sauce")

        # Bấm nút burger menu
        menu_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "react-burger-menu-btn")))
        menu_btn.click()

        # Chờ nút Logout trong sidebar hiển thị và có thể click
        logout_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
        logout_btn.click()

        # Kiểm tra đã trở về trang đăng nhập
        login_button = self.wait.until(EC.visibility_of_element_located((By.ID, "login-button")))
        self.assertTrue(login_button.is_displayed(), "Không tìm thấy nút Login sau khi đăng xuất!")
        self.assertNotIn("/inventory.html", self.driver.current_url, "Vẫn đang ở trang sản phẩm sau khi đăng xuất!")

        self.take_screenshot("TC06_Logout_Success")
        print("  -> PASS: Đăng xuất thành công, đã trở về màn hình đăng nhập.")


if __name__ == "__main__":
    # Tùy chỉnh xuất báo cáo tổng kết đẹp mắt
    print("=" * 80)
    print(" BẮT ĐẦU CHẠY BỘ KIỂM THỬ TỰ ĐỘNG SELENIUM TRÊN SAUCEDEMO")
    print("=" * 80)

    # Lọc bỏ cờ tùy chỉnh để unittest.main không báo lỗi unrecognized arguments
    custom_args = [arg for arg in sys.argv if not arg.startswith("--headless")]
    sys.argv = custom_args

    suite = unittest.TestLoader().loadTestsFromTestCase(TestSauceDemoSuite)
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print("\n" + "=" * 80)
    print(" BÁO CÁO TỔNG KẾT KIỂM THỬ (TEST SUMMARY REPORT)")
    print("=" * 80)
    print(f" Tổng số test case thực thi : {result.testsRun}")
    print(f" Số test case THÀNH CÔNG    : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" Số test case THẤT BẠI      : {len(result.failures)}")
    print(f" Số test case LỖI           : {len(result.errors)}")
    print(f" Thời gian thực thi         : {elapsed:.2f} giây")
    print(f" Ảnh chụp màn hình tại      : {SCREENSHOTS_DIR}")
    print("=" * 80)

    sys.exit(0 if result.wasSuccessful() else 1)
