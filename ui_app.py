from nicegui import ui
import requests

API_URL = "http://127.0.0.1:8000"
auth_token = {"token": None}

@ui.page('/')
def main_page():
    ui.label('Flight Price Comparison App').classes('text-2xl font-bold mb-4 text-primary')
    
    with ui.tabs() as tabs:
        login_tab = ui.tab('Login')
        signup_tab = ui.tab('Signup')
        
    with ui.tab_panels(tabs, value=login_tab).classes('w-full max-w-md mx-auto'):
        
        # --- LOGIN PANEL ---
        with ui.tab_panel(login_tab):
            with ui.card().classes('w-full p-4'):
                ui.label('User Login').classes('text-xl font-semibold mb-2')
                l_user = ui.input('Username / Email').classes('w-full')
                l_pass = ui.input('Password', password=True, password_toggle_button=True).classes('w-full')
                
                def handle_login():
                    try:
                        res = requests.post(f"{API_URL}/token", data={"username": l_user.value, "password": l_pass.value})
                        if res.status_code == 200:
                            auth_token["token"] = res.json()["access_token"]
                            ui.notify('Login successful!', type='positive')
                            ui.navigate.to('/dashboard')
                        else:
                            ui.notify('Invalid username or password', type='negative')
                    except Exception as e:
                        ui.notify(f'Error: {e}', type='negative')

                ui.button('Login', on_click=handle_login).classes('w-full mt-4 bg-blue-500 text-white')

        # --- SIGNUP PANEL ---
        with ui.tab_panel(signup_tab):
            with ui.card().classes('w-full p-4'):
                ui.label('Create New Account').classes('text-xl font-semibold mb-2')
                s_user = ui.input('Username').classes('w-full')
                s_email = ui.input('Email').classes('w-full')
                s_pass = ui.input('Password', password=True, password_toggle_button=True).classes('w-full')
                
                def handle_signup():
                    try:
                        payload = {"username": s_user.value, "email": s_email.value, "password": s_pass.value}
                        res = requests.post(f"{API_URL}/users/", json=payload)
                        if res.status_code in [200, 201]:
                            ui.notify('Signup successful! Please login now.', type='positive')
                        else:
                            ui.notify(f'Signup failed: {res.text}', type='negative')
                    except Exception as e:
                        ui.notify(f'Error: {e}', type='negative')

                ui.button('Sign Up', on_click=handle_signup).classes('w-full mt-4 bg-green-500 text-white')

@ui.page('/dashboard')
def dashboard():
    if not auth_token["token"]:
        ui.label('Unauthorized. Please log in first.').classes('text-red-500 text-lg')
        ui.button('Go to Login', on_click=lambda: ui.navigate.to('/')).classes('mt-2')
        return

    ui.label('Flight Price Comparison Dashboard').classes('text-2xl font-bold mb-4')
    
    with ui.card().classes('w-full p-6'):
        ui.label('Search & Compare Flights').classes('text-xl font-semibold mb-4')
        
        def add_sample_flight():
            headers = {"Authorization": f"Bearer {auth_token['token']}"}
            sample = {
                "airline_name": "IndiGo",
                "source": "Delhi",
                "destination": "Mumbai",
                "price": 4500.0,
                "flight_date": "2026-06-15"
            }
            res = requests.post(f"{API_URL}/flights/", json=sample, headers=headers)
            if res.status_code in [200, 201]:
                ui.notify('Sample flight added!', type='positive')
                load_flights()
            else:
                ui.notify(f'Error adding sample: {res.text}', type='negative')

        ui.button('Add Sample Flight (IndiGo)', on_click=add_sample_flight).classes('mb-4 bg-purple-500 text-white')
        
        with ui.row().classes('w-full gap-4 mb-4'):
            search_source = ui.input('From (Source)').classes('flex-1')
            search_dest = ui.input('To (Destination)').classes('flex-1')
            
        table = ui.table(
            columns=[
                {'name': 'airline', 'label': 'Airline', 'field': 'airline_name', 'align': 'left'},
                {'name': 'source', 'label': 'From', 'field': 'source', 'align': 'left'},
                {'name': 'destination', 'label': 'To', 'field': 'destination', 'align': 'left'},
                {'name': 'price', 'label': 'Price (INR)', 'field': 'price', 'sortable': True, 'align': 'right'},
                {'name': 'date', 'label': 'Date', 'field': 'flight_date', 'align': 'center'},
            ],
            rows=[]
        ).classes('w-full')

        all_flights = []

        def load_flights():
            nonlocal all_flights
            try:
                res = requests.get(f"{API_URL}/flights/")
                if res.status_code == 200:
                    all_flights = res.json()
                    table.rows[:] = all_flights
                    table.update()
                else:
                    ui.notify('Could not load flights', type='negative')
            except Exception as e:
                ui.notify(f'Error: {e}', type='negative')

        def filter_flights():
            src = search_source.value.strip().lower()
            dst = search_dest.value.strip().lower()
            
            filtered = [
                f for f in all_flights 
                if (not src or src in f['source'].lower()) and (not dst or dst in f['destination'].lower())
            ]
            table.rows[:] = filtered
            table.update()

        with ui.row().classes('gap-2 mb-4'):
            ui.button('Search', on_click=filter_flights).classes('bg-blue-500 text-white')
            ui.button('Reset', on_click=lambda: (setattr(search_source, 'value', ''), setattr(search_dest, 'value', ''), load_flights())).classes('bg-gray-400 text-white')

        load_flights()

ui.run(port=8080)