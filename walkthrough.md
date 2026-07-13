# Java Database Programs Walkthrough

I have successfully generated two Java Core applications with real-time Database interactions for you. Both programs follow the standard MVC/Layered architecture (Model, DAO, Service, Main).

The code and setup scripts have been placed in your requested directory:
`c:\Users\Aviral Bansal\Downloads\Random\Db_programs`

## 1. Bank Transaction Manager (`Program1_Bank`)
This program simulates banking transactions, specifically focusing on how to securely handle Database Transactions using ACID principles.
- **Key Feature:** Disables auto-commit to perform complex transfers. If an account doesn't have enough funds, the transaction is `rollback()`-ed safely to avoid data corruption. 

## 2. E-Commerce Inventory Tracker (`Program2_Inventory`)
This program simulates checking out items from an online store's inventory.
- **Key Feature:** Performs `JOIN` queries to merge Product and Category data, runs Aggregate functions (`SUM`) to calculate inventory values, and uses Conditional Updates (`stock_quantity >= ?`) to safely reduce stock in a concurrent environment.

## 3. Employee Management System (`Program3_Employee`)
This program demonstrates managing employee records and applying department-wide updates.
- **Key Feature:** Performs Batch Updates by safely increasing salaries across a department based on a calculated percentage using a single parameter. 

## 4. Library Book Checkout System (`Program4_Library`)
This program simulates borrowing books from a library, demonstrating complex multi-table transaction updates.
- **Key Feature:** Manages Foreign Key dependencies and multi-statement transactions. Safely reduces book availability (checking if copies > 0) and inserts checkout records, ensuring data consistency with `commit` and `rollback`.

---

## 🛠️ How to Set Up in Eclipse

Follow these steps to import and run the code on your work laptop:

> [!IMPORTANT]
> **Prerequisite:** Ensure you have downloaded the **MySQL Connector/J JAR** file (e.g., `mysql-connector-j-8.x.x.jar`).

### Step 1: Run the Setup SQL Scripts
1. Open **MySQL Workbench**.
2. Open the SQL script files generated in the root of each program folder (`bank_setup.sql` and `inventory_setup.sql`).
3. Run the scripts. This will automatically create the schemas (`demo_bank`, `demo_inventory`), tables, and populate them with dummy data.

### Step 2: Create the Eclipse Projects
1. In Eclipse, go to **File -> New -> Java Project**. Name it `Program1_Bank`.
2. Do the same for `Program2_Inventory`.

### Step 3: Copy Code and Add Dependencies
1. Copy the `com` folder from `Program1_Bank\src` into your new Eclipse project's `src` folder. Repeat for Program 2.
2. In Eclipse, right-click on the Project in the Package Explorer.
3. Select **Build Path -> Configure Build Path...**
4. Go to the **Libraries** tab -> **Classpath** -> Click **Add External JARs...**
5. Select your downloaded `mysql-connector-j-x.x.x.jar` file and click Apply.

> [!WARNING]
> Don't forget to update the database credentials in `DatabaseConnection.java` for both projects! The code currently defaults to `root`/`root`.

### Step 4: Run the Programs
1. Navigate to the `BankMain.java` and `InventoryMain.java` files.
2. Right-click the file -> **Run As -> Java Application**.
3. Watch the console output to see the real-time Database Interactions in action!
