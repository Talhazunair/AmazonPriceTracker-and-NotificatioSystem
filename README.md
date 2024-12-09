# AmazonPriceTracker-and-NotificatioSystem

The Amazon Price Tracker is a Python script that tracks the price of products on Amazon and sends notifications when the price drops below a target threshold. It also stores price history in a CSV file for later analysis. This guide provides an overview of the script's features, setup instructions, and usage.

## Features

- **Automated Price Tracking**: Monitors product prices on Amazon.
- **Captcha Solver**: Automatically solves CAPTCHA challenges using EasyOCR.
- **Notifications**: Sends desktop notifications when the price is below a specified threshold.
- **Multiple Products Support**: Tracks prices for multiple products listed in a text file.
- **Price History Logging**: Stores price history in a CSV file.

## Requirements

- Python 3.7+
- Google Chrome
- ChromeDriver
- Required Python Libraries:
  - `selenium`
  - `requests`
  - `plyer`
  - `easyocr`
  - `Pillow`
  - `csv`

## Installation

1. **Install Dependencies**:

   ```bash
   pip install selenium requests plyer easyocr Pillow
   ```

2. **Download ChromeDriver**:

   - Ensure the ChromeDriver version matches your installed Google Chrome version.
   - Download it from [ChromeDriver](https://sites.google.com/chromium.org/driver/).
   - Add the downloaded `chromedriver` to your system PATH.

3. **Create Required Files**:

   - Create a `products.txt` file and list Amazon product URLs (one per line).

## Usage

### Script Overview

#### 1. **Initialize the Tracker**

The `AmazonPriceTracker` class is initialized with a Selenium WebDriver setup.

```python
tracker = AmazonPriceTracker()
```

#### 2. **Track a Single Product**

Track the price of a single product by providing the product URL:

```python
tracker.track_price("<product_url>")
```

#### 3. **Track Multiple Products**

Track prices for multiple products listed in a text file:

```python
tracker.multiple_products("products.txt")
```

#### 4. **Set Price Alerts**

Set a target price and receive notifications if the product price drops below it:

```python
tracker.set_price_alert(149)
```

#### 5. **Save Price History**

Store the product price and title in a CSV file:

```python
tracker.save_price_history(current_price, product_title)
```

### Running the Script

Run the script in an infinite loop to check prices periodically:

```
python main.py
```

### Sample Output

1. Desktop notification:
   - **Title**: "Amazon Price Tracker - "
   - **Message**: "The Current Price is: \$"
2. CSV file `price_history.csv` with columns:
   - Timestamp
   - Product Title
   - Current Price

### Example

#### Input (`products.txt`):

```
https://www.amazon.com/dp/example_product_1
https://www.amazon.com/dp/example_product_2
```

#### Output (`price_history.csv`):

| Timestamp           | Product Title           | Current Price |
| ------------------- | ----------------------- | ------------- |
| 2024-12-09 10:00:00 | Example Product 1 Title | 129           |
| 2024-12-09 10:05:00 | Example Product 2 Title | 199           |

## Notes

- The script uses a CAPTCHA solver based on EasyOCR to handle Amazon CAPTCHA challenges.
- Ensure your system meets all requirements and dependencies are installed.
- Adjust the `time.sleep()` interval in the main loop for frequent or less frequent checks.

## Limitations

- OCR accuracy may vary depending on the complexity of CAPTCHA images.
- Amazon may block excessive requests; consider implementing proxy support to avoid detection.

## License

This project is licensed under the MIT License. Feel free to use and modify it as per your requirements.

## Contributions

Contributions, issues, and feature requests are welcome! Please feel free to open a pull request or issue on GitHub.

