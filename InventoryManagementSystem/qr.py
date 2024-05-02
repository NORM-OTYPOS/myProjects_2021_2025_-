import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

# Font for displaying QR code data
font = cv2.FONT_HERSHEY_PLAIN

# Open the laptop webcam
cap = cv2.VideoCapture(0)

# Inventory data
inventory = [
    {"serialNo": "001", "name": "Raw Material A", "quantity": 20},
    {"serialNo": "002", "name": "Raw Material B", "quantity": 5},
    {"serialNo": "003", "name": "Raw Material C", "quantity": 15},
    {"serialNo": "004", "name": "Raw Material D", "quantity": 8}
]

# Threshold value for low quantity
low_threshold = 10

# Function to update the HTML table with the updated inventory data
def update_inventory_table(item):
    inventory_html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Inventory Dashboard</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            .low {
                color: red;
                font-weight: bold;
            }
            .navbar {
                background-color: #1e90ff; /* Updated blue color for the navbar */
            }
            .card-header {
                background-color: #1e90ff; /* Updated blue color for the card header */
                color: #fff; /* White text color */
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="#">Inventory Dashboard</a>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="card">
                <div class="card-header">
                    <h4>Inventory</h4>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Serial No.</th>
                                <th>Name</th>
                                <th>Quantity</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="inventoryTable">
                            </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        <script>
            // Function to create a table row for an inventory item
            function createInventoryRow(item) {
                const row = document.createElement('tr');

                const serialNoCell = document.createElement('td');
                serialNoCell.textContent = item.serialNo;
                row.appendChild(serialNoCell);

                const nameCell = document.createElement('td');
                nameCell.textContent = item.name;
                row.appendChild(nameCell);

                const quantityCell = document.createElement('td');
                quantityCell.textContent = item.quantity;
                row.appendChild(quantityCell);

                const statusCell = document.createElement('td');
                const status = item.quantity < lowThreshold ? 'Low' : 'High';
                statusCell.textContent = status;
                if (status === 'Low') {
                    statusCell.classList.add('low');
                }
                row.appendChild(statusCell);

                return row;
            }

            // Update the table content based on the updated item data
            const inventoryTable = document.getElementById('inventoryTable');
            inventoryTable.innerHTML = '';
            const lowThreshold = """ + str(low_threshold) + """;
            const inventory = """ + str(inventory) + """;
            inventory.forEach(item => {
                const row = createInventoryRow(item);
                inventoryTable.appendChild(row);
            });
        </script>
    </body>
    </html>
    """

    # Find the table row for the updated item and modify its content
    with open('database.html', 'w') as f:
        f.write(inventory_html_content)

# Function to increment the quantity of an item based on serial number
def increment_item_quantity(serial_number):
    for item in inventory:
        if item["serialNo"] == serial_number:
            item["quantity"] += 1
            update_inventory_table(item)
            print(f"Quantity incremented for {item['name']} (Serial No. {item['serialNo']})")
            return True
    print(f"No item found with Serial No. {serial_number}")
    return False

# Open the "live transmission" window
cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)

prev = ""
pres = ""

while True:
    _, frame = cap.read()

    decoded_objects = pyzbar.decode(frame)
    for obj in decoded_objects:
        pres = obj.data
        if prev == pres:
            pass
        else:
            print("Type:", obj.type)
            print("Data: ", obj.data)
            prev = pres

            # Increment the quantity based on the scanned serial number
            serial_number = obj.data.decode("utf-8")
            increment_item_quantity(serial_number)

        cv2.putText(frame, str(obj.data), (50, 50), font, 2, (255, 0, 0), 3)

    cv2.imshow("live transmission", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()