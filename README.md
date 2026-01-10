# Fulfillment App

A simple Django app to manage order fulfillment.

## Setup

1.  **Install dependencies** (already done if you followed the setup):
    ```bash
    pip install django pandas
    ```

2.  **Initialize Database**:
    ```bash
    python manage.py migrate
    ```

3.  **Import Orders**:
    There is a custom management command to import orders from `orders_export.csv`.
    ```bash
    python manage.py import_orders
    ```

## Running the App

Start the server:
```bash
python manage.py runserver
```

Open your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

- **To Do**: Lists unfulfilled orders.
- **Completed**: Lists fulfilled orders.
- Click "Mark Complete" to move an order to the Completed list.
- Click "Undo" to move it back.

## Updates

To add more orders, update `orders_export.csv` and run `python manage.py import_orders` again.
