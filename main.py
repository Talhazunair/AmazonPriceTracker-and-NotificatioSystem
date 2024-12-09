import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttk
import threading
import os
import sys
import time
import csv
import queue

# Import the existing AmazonPriceTracker class
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from AmazonPriceTracker import AmazonPriceTracker

class QueueHandler:
    def __init__(self, queue, text_widget):
        self.queue = queue
        self.text_widget = text_widget
        self.text_widget.tag_config('error', foreground='red')
        self.text_widget.tag_config('success', foreground='green')
        self.text_widget.tag_config('info', foreground='white')

    def process_messages(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg[0] == 'error':
                    self.text_widget.insert(tk.END, msg[1] + '\n', 'error')
                elif msg[0] == 'success':
                    self.text_widget.insert(tk.END, msg[1] + '\n', 'success')
                else:
                    self.text_widget.insert(tk.END, msg[1] + '\n', 'info')
                self.text_widget.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.text_widget.after(100, self.process_messages)

class AmazonPriceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Price Tracker")
        self.root.geometry("800x800")
        
        # Tracking control
        self.is_tracking = False
        self.tracking_thread = None
        
        # Message queue for live updates
        self.message_queue = queue.Queue()
        
        # Create tracker instance
        self.tracker = AmazonPriceTracker()
        
        # Style
        self.style = ttk.Style(theme='superhero')
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        self.title_label = ttk.Label(
            self.main_container, 
            text="Amazon Price Tracker", 
            font=('Helvetica', 20, 'bold'),
            bootstyle='inverse-primary'
        )
        self.title_label.pack(pady=(0, 20))
        
        # Product URL Input
        self.url_frame = ttk.Frame(self.main_container)
        self.url_frame.pack(fill=tk.X, pady=10)
        
        self.url_label = ttk.Label(self.url_frame, text="Product URL:", font=('Helvetica', 12))
        self.url_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.url_entry = ttk.Entry(self.url_frame, width=50, font=('Helvetica', 10))
        self.url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        # Target Price Input
        self.price_frame = ttk.Frame(self.main_container)
        self.price_frame.pack(fill=tk.X, pady=10)
        
        self.price_label = ttk.Label(self.price_frame, text="Target Price ($):", font=('Helvetica', 12))
        self.price_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.price_entry = ttk.Entry(self.price_frame, width=20, font=('Helvetica', 10))
        self.price_entry.pack(side=tk.LEFT)
        
        # File Selection
        self.file_frame = ttk.Frame(self.main_container)
        self.file_frame.pack(fill=tk.X, pady=10)
        
        self.file_label = ttk.Label(self.file_frame, text="Products File:", font=('Helvetica', 12))
        self.file_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, width=40, font=('Helvetica', 10))
        self.file_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        self.browse_button = ttk.Button(
            self.file_frame, 
            text="Browse", 
            command=self.browse_file,
            bootstyle='secondary'
        )
        self.browse_button.pack(side=tk.LEFT)
        
        # Buttons Frame
        self.buttons_frame = ttk.Frame(self.main_container)
        self.buttons_frame.pack(fill=tk.X, pady=20)
        
        self.track_single_button = ttk.Button(
            self.buttons_frame, 
            text="Track Single Product", 
            command=self.track_single_product,
            bootstyle='success'
        )
        self.track_single_button.pack(side=tk.LEFT, padx=10)
        
        self.track_multiple_button = ttk.Button(
            self.buttons_frame, 
            text="Track Multiple Products", 
            command=self.track_multiple_products,
            bootstyle='primary'
        )
        self.track_multiple_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = ttk.Button(
            self.buttons_frame, 
            text="Stop Tracking", 
            command=self.stop_tracking,
            bootstyle='danger'
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Live Message Area
        self.message_label = ttk.Label(
            self.main_container, 
            text="Live Messages", 
            font=('Helvetica', 16, 'bold'),
            bootstyle='inverse-primary'
        )
        self.message_label.pack(pady=(20, 10))
        
        # Message Text Widget
        self.message_frame = ttk.Frame(self.main_container)
        self.message_frame.pack(fill=tk.BOTH, expand=True)
        
        self.message_scroll = ttk.Scrollbar(self.message_frame)
        self.message_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.message_text = tk.Text(
            self.message_frame, 
            height=10, 
            width=80, 
            wrap=tk.WORD,
            font=('Consolas', 10)
        )
        self.message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.message_scroll.config(command=self.message_text.yview)
        self.message_text.config(yscrollcommand=self.message_scroll.set)
        
        # Set up message queue handler
        self.queue_handler = QueueHandler(self.message_queue, self.message_text)
        self.queue_handler.process_messages()
        
        # Price History
        self.history_label = ttk.Label(
            self.main_container, 
            text="Price History", 
            font=('Helvetica', 16, 'bold'),
            bootstyle='inverse-primary'
        )
        self.history_label.pack(pady=(20, 10))
        
        # Treeview for Price History
        self.tree_frame = ttk.Frame(self.main_container)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            self.tree_frame, 
            columns=('Timestamp', 'Product', 'Price'), 
            show='headings',
            yscrollcommand=self.tree_scroll.set
        )
        
        # Define headings
        self.tree.heading('Timestamp', text='Timestamp')
        self.tree.heading('Product', text='Product')
        self.tree.heading('Price', text='Price')
        
        # Define column widths
        self.tree.column('Timestamp', width=200)
        self.tree.column('Product', width=300)
        self.tree.column('Price', width=100)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.tree.yview)
        
        # Populate initial price history
        self.load_price_history()
    
    def log_message(self, msg_type, message):
        """Add message to the queue for display"""
        self.message_queue.put((msg_type, message))
    
    def browse_file(self):
        """Open file dialog to select products file"""
        filename = filedialog.askopenfilename(
            title="Select Products File",
            filetypes=[("Text files", "*.txt")]
        )
        if filename:
            self.file_path.set(filename)
    
    def stop_tracking(self):
        """Stop the current tracking process"""
        if self.is_tracking and self.tracking_thread:
            self.is_tracking = False
            self.log_message('error', 'Tracking process stopped by user.')
            
            # Close the browser if it's open
            try:
                self.tracker.driver.quit()
            except:
                pass
            
            # Wait for thread to finish
            if self.tracking_thread.is_alive():
                self.tracking_thread.join()
    
    def track_single_product(self):
        """Track a single product from URL"""
        url = self.url_entry.get()
        target_price = self.price_entry.get()
        
        if not url or not target_price:
            messagebox.showerror("Error", "Please enter both URL and Target Price")
            return
        
        # Reset tracking flag
        self.is_tracking = True
        
        # Clear previous messages
        self.message_text.delete(1.0, tk.END)
        
        # Run in a separate thread to prevent GUI freezing
        self.tracking_thread = threading.Thread(
            target=self._track_single_product, 
            args=(url, target_price), 
            daemon=True
        )
        self.tracking_thread.start()
    
    def _track_single_product(self, url, target_price):
        """Internal method to track single product"""
        try:
            # Override driver's print methods to log messages
            original_print = print
            def custom_print(*args, **kwargs):
                message = ' '.join(map(str, args))
                
                if "Captcha Solved Successfully" in message:
                    self.log_message('success', message)
                elif "Captcha Not Required" in message:
                    self.log_message('info', message)
                elif "Captcha Not Solved" in message:
                    self.log_message('error', message)
                else:
                    self.log_message('info', message)
                
                original_print(*args, **kwargs)
            
            # Temporarily replace print
            __builtins__['print'] = custom_print
            
            # Log start of tracking
            self.log_message('info', f'Starting to track product: {url}')
            
            # Track the product
            self.tracker.track_price(url)
            self.tracker.set_price_alert(int(target_price))
            
            # Reload price history
            self.root.after(0, self.load_price_history)
            
            # Log completion
            self.log_message('success', 'Product tracking completed successfully.')
        
        except Exception as e:
            self.log_message('error', f'Tracking Error: {str(e)}')
        
        finally:
            # Restore original print
            __builtins__['print'] = original_print
            
            # Update tracking flag
            self.is_tracking = False
    
    def track_multiple_products(self):
        """Track multiple products from file"""
        file_path = self.file_path.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a products file")
            return
        
        # Reset tracking flag
        self.is_tracking = True
        
        # Clear previous messages
        self.message_text.delete(1.0, tk.END)
        
        # Run in a separate thread to prevent GUI freezing
        self.tracking_thread = threading.Thread(
            target=self._track_multiple_products, 
            args=(file_path,), 
            daemon=True
        )
        self.tracking_thread.start()
    
    def _track_multiple_products(self, file_path):
        """Internal method to track multiple products"""
        try:
            # Store the original print function
            original_print = print
            
            def custom_print(*args, **kwargs):
                message = ' '.join(map(str, args))
                
                if "Captcha Solved Successfully" in message:
                    self.log_message('success', message)
                elif "Captcha Not Required" in message:
                    self.log_message('info', message)
                elif "Captcha Not Solved" in message:
                    self.log_message('error', message)
                else:
                    self.log_message('info', message)
                
                original_print(*args, **kwargs)
            
            # Temporarily replace the built-in print function
            import builtins
            builtins.print = custom_print
            
            # Open the file and read URLs
            with open(file_path, 'r') as f:
                urls = f.readlines()
            
            # Log start of tracking
            self.log_message('info', f'Starting to track {len(urls)} products')
            
            # Track each product
            for i, url in enumerate(urls, 1):
                if not self.is_tracking:
                    self.log_message('error', 'Tracking stopped by user.')
                    break
                
                url = url.strip()
                self.log_message('info', f'Tracking Product {i}/{len(urls)}: {url}')
                
                try:
                    self.tracker.track_price(url)
                except Exception as e:
                    self.log_message('error', f'Error tracking product {i}: {str(e)}')
            
            # Reload price history
            self.root.after(0, self.load_price_history)
            
            # Log completion
            self.log_message('success', 'Multiple product tracking completed.')
        
        except Exception as e:
            self.log_message('error', f'Tracking Error: {str(e)}')
        
        finally:
            # Restore original print function
            import builtins
            builtins.print = original_print
            
            # Update tracking flag
            self.is_tracking = False
    
    def load_price_history(self):
        """Load price history from CSV into treeview"""
        # Clear existing items
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Check if price history file exists
        if not os.path.exists('price_history.csv'):
            return
        
        # Read and populate price history
        try:
            with open('price_history.csv', 'r') as f:
                # Use csv reader to handle quoted fields correctly
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    # Ensure we have at least 3 columns
                    if len(row) >= 3:
                        timestamp = row[0]
                        product = row[1]
                        price = row[2]
                        self.tree.insert('', 'end', values=(timestamp, product, price))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load price history: {e}")

def main():
    root = ttk.Window(themename="superhero")
    app = AmazonPriceTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()