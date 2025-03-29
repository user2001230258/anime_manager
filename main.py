import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
from datetime import datetime
import os
from PIL import Image, ImageTk
from io import BytesIO
import threading
import time
from functools import lru_cache

class AnimeManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Anime Manager")
        self.window.geometry("1200x800")
        
        # Initialize data files
        self.initialize_data_files()
        self.image_cache = {}
        self.current_display_list = []  # Store current displayed anime list
        self.api_cache = {}  # Cache for API responses
        
        # Start with login screen
        self.show_login_screen()

    def initialize_data_files(self):
        # Initialize users.json if not exists
        if not os.path.exists('users.json'):
            default_users = {
                "admin": {
                    "password": "admin123",
                    "role": "admin",
                    "favorites": []
                },
                "user": {
                    "password": "user123",
                    "role": "user",
                    "favorites": []
                }
            }
            with open('users.json', 'w') as f:
                json.dump(default_users, f, indent=4)

        # Initialize anime_data.json if not exists
        if not os.path.exists('anime_data.json'):
            with open('anime_data.json', 'w') as f:
                json.dump([], f)

    def show_loading_screen(self):
        """Show loading overlay"""
        self.loading_frame = ttk.Frame(self.window, style='Loading.TFrame')
        self.loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        loading_label = ttk.Label(self.loading_frame, text="Loading...", font=('Arial', 14))
        loading_label.place(relx=0.5, rely=0.5, anchor='center')

    def hide_loading_screen(self):
        """Hide loading overlay"""
        if hasattr(self, 'loading_frame'):
            self.loading_frame.destroy()

    def background_task(self, task, *args):
        """Execute task in background thread"""
        self.show_loading_screen()
        try:
            result = task(*args)
            self.window.after(0, lambda: self.task_completed(result))
        except Exception as e:
            self.window.after(0, lambda: self.task_failed(str(e)))

    def task_completed(self, result):
        """Handle task completion"""
        self.hide_loading_screen()
        if result:
            self.current_display_list = result
            self.display_anime_grid(result)

    def task_failed(self, error_message):
        """Handle task failure"""
        self.hide_loading_screen()
        messagebox.showerror("Error", error_message)

    def show_login_screen(self):
        # Clear window
        for widget in self.window.winfo_children():
            widget.destroy()

        # Create login frame
        login_frame = ttk.Frame(self.window)
        login_frame.pack(expand=True)

        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        username_entry = ttk.Entry(login_frame)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(login_frame, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Login button
        ttk.Button(login_frame, text="Login", 
                  command=lambda: self.login(username_entry.get(), password_entry.get())
                  ).grid(row=2, column=0, columnspan=2, pady=10)

        # Register button
        ttk.Button(login_frame, text="Register", 
                  command=self.show_register_screen
                  ).grid(row=3, column=0, columnspan=2)

    def show_register_screen(self):
        # Clear window
        for widget in self.window.winfo_children():
            widget.destroy()

        # Create register frame
        register_frame = ttk.Frame(self.window)
        register_frame.pack(expand=True)

        # Username
        ttk.Label(register_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        username_entry = ttk.Entry(register_frame)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        # Password
        ttk.Label(register_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(register_frame, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Confirm Password
        ttk.Label(register_frame, text="Confirm Password:").grid(row=2, column=0, padx=5, pady=5)
        confirm_password_entry = ttk.Entry(register_frame, show="*")
        confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)

        def register():
            username = username_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()

            if not username or not password or not confirm_password:
                messagebox.showerror("Error", "Please fill all fields")
                return

            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return

            with open('users.json', 'r') as f:
                users = json.load(f)

            if username in users:
                messagebox.showerror("Error", "Username already exists")
                return

            users[username] = {
                "password": password,
                "role": "user",
                "favorites": []
            }

            with open('users.json', 'w') as f:
                json.dump(users, f, indent=4)

            messagebox.showinfo("Success", "Registration successful!")
            self.show_login_screen()

        # Register button
        ttk.Button(register_frame, text="Register", 
                  command=register
                  ).grid(row=3, column=0, columnspan=2, pady=10)

        # Back to login button
        ttk.Button(register_frame, text="Back to Login", 
                  command=self.show_login_screen
                  ).grid(row=4, column=0, columnspan=2)

    def login(self, username, password):
        with open('users.json', 'r') as f:
            users = json.load(f)

        if username in users and users[username]["password"] == password:
            self.current_user = username
            self.current_role = users[username]["role"]
            self.current_user_favorites = users[username].get("favorites", [])
            self.show_main_screen()
            # Fetch top anime after successful login
            threading.Thread(target=lambda: self.background_task(self.fetch_top_anime)).start()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def show_main_screen(self):
        # Clear window
        for widget in self.window.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Create search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=5)

        ttk.Label(search_frame, text="Search Anime:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side='left', padx=5)
        
        # Add search binding to Enter key
        self.search_entry.bind('<Return>', lambda e: self.search_anime_api())
        
        ttk.Button(search_frame, text="Search", 
                  command=self.search_anime_api
                  ).pack(side='left', padx=5)

        # Create view selection frame
        view_frame = ttk.Frame(main_frame)
        view_frame.pack(fill='x', pady=5)

        view_var = tk.StringVar(value="all")
        ttk.Radiobutton(view_frame, text="All Anime", variable=view_var, 
                       value="all", command=lambda: self.display_anime_grid(self.current_display_list)
                       ).pack(side='left', padx=5)
        ttk.Radiobutton(view_frame, text="Favorites", variable=view_var,
                       value="favorites", command=self.show_favorites
                       ).pack(side='left', padx=5)

        # Create content frame with canvas for scrolling
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill='both')

        canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Refresh Top Anime", 
                  command=lambda: threading.Thread(target=lambda: self.background_task(self.fetch_top_anime)).start()
                  ).pack(side='left', padx=5)

        ttk.Button(button_frame, text="Logout", 
                  command=self.show_login_screen
                  ).pack(side='right', padx=5)

    @lru_cache(maxsize=100)
    def fetch_image(self, url):
        """Cache and fetch images"""
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content))
            image = image.resize((200, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            return photo
        except Exception:
            return None

    def fetch_top_anime(self):
        try:
            # Check cache first
            cache_key = "top_anime"
            if cache_key in self.api_cache:
                return self.api_cache[cache_key]

            # Add delay for API rate limiting
            time.sleep(0.5)
            
            # Fetch top anime from Jikan API
            response = requests.get("https://api.jikan.moe/v4/top/anime")
            if response.status_code != 200:
                raise Exception("Failed to fetch data from API")

            anime_data = response.json()['data']
            
            # Process results
            processed_anime = []
            for anime in anime_data[:20]:  # Limit to 20 anime
                processed_anime.append({
                    'title': anime['title'],
                    'rating': str(anime.get('score', 'N/A')),
                    'episodes': str(anime.get('episodes', 'N/A')),
                    'status': anime.get('status', 'N/A'),
                    'image_url': anime.get('images', {}).get('jpg', {}).get('image_url', '')
                })

            # Cache the results
            self.api_cache[cache_key] = processed_anime
            
            # Save to JSON
            with open('anime_data.json', 'w') as f:
                json.dump(processed_anime, f, indent=4)

            return processed_anime

        except Exception as e:
            raise Exception(f"Failed to fetch anime data: {str(e)}")

    def search_anime_api(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term")
            return

        def search_task():
            try:
                # Check cache first
                cache_key = f"search_{query}"
                if cache_key in self.api_cache:
                    return self.api_cache[cache_key]

                # Add delay for API rate limiting
                time.sleep(0.5)
                
                # Search anime using Jikan API
                response = requests.get(f"https://api.jikan.moe/v4/anime", params={'q': query})
                if response.status_code != 200:
                    raise Exception("Failed to fetch data from API")

                anime_data = response.json()['data']
                
                if not anime_data:
                    return []

                # Process results
                processed_anime = []
                for anime in anime_data[:20]:  # Limit to 20 results
                    processed_anime.append({
                        'title': anime['title'],
                        'rating': str(anime.get('score', 'N/A')),
                        'episodes': str(anime.get('episodes', 'N/A')),
                        'status': anime.get('status', 'N/A'),
                        'image_url': anime.get('images', {}).get('jpg', {}).get('image_url', '')
                    })

                # Cache the results
                self.api_cache[cache_key] = processed_anime
                return processed_anime

            except Exception as e:
                raise Exception(f"Failed to search anime: {str(e)}")

        threading.Thread(target=lambda: self.background_task(search_task)).start()

    def display_anime_grid(self, anime_list):
        if not anime_list:
            messagebox.showinfo("Result", "No anime found")
            return

        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        row = 0
        col = 0
        max_cols = 3

        for anime in anime_list:
            # Create frame for each anime
            anime_frame = ttk.Frame(self.scrollable_frame)
            anime_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Create border frame
            border_frame = ttk.Frame(anime_frame, style='Card.TFrame')
            border_frame.pack(expand=True, fill='both', padx=2, pady=2)

            # Load and display image
            image_url = anime.get('image_url', '')
            if image_url:
                photo = self.fetch_image(image_url)
                if photo:
                    image_label = ttk.Label(border_frame, image=photo)
                    image_label.image = photo
                    image_label.pack(pady=5)
                else:
                    ttk.Label(border_frame, text="Image not available").pack(pady=5)

            # Display title
            title_label = ttk.Label(border_frame, text=anime['title'], wraplength=200)
            title_label.pack(pady=5)

            # Display rating and episodes
            info_text = f"Rating: {anime.get('rating', 'N/A')}\nEpisodes: {anime.get('episodes', 'N/A')}"
            ttk.Label(border_frame, text=info_text).pack(pady=5)

            # Favorite button
            is_favorite = anime['title'] in self.current_user_favorites
            favorite_text = "♥" if is_favorite else "♡"
            
            favorite_btn = tk.Button(
                border_frame, 
                text=favorite_text,
                command=lambda a=anime: self.toggle_favorite(a),
                relief="flat",
                font=("Arial", 12),
                fg="red" if is_favorite else "gray",
                bg="white",
                width=2,
                height=1
            )
            favorite_btn.pack(pady=5)

            # Update grid position
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def toggle_favorite(self, anime):
        try:
            with open('users.json', 'r') as f:
                users = json.load(f)

            if 'favorites' not in users[self.current_user]:
                users[self.current_user]['favorites'] = []

            if anime['title'] in users[self.current_user]['favorites']:
                users[self.current_user]['favorites'].remove(anime['title'])
            else:
                users[self.current_user]['favorites'].append(anime['title'])

            with open('users.json', 'w') as f:
                json.dump(users, f, indent=4)

            self.current_user_favorites = users[self.current_user]['favorites']
            
            # Refresh the current view without reloading
            self.display_anime_grid(self.current_display_list)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update favorites: {str(e)}")

    def show_favorites(self):
        try:
            favorite_anime = [
                anime for anime in self.current_display_list 
                if anime['title'] in self.current_user_favorites
            ]
            self.display_anime_grid(favorite_anime)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load favorites: {str(e)}")

    def run(self):
        # Configure style for frames
        style = ttk.Style()
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        style.configure('Loading.TFrame', background='white')
        
        self.window.mainloop()

if __name__ == "__main__":
    app = AnimeManager()
    app.run()