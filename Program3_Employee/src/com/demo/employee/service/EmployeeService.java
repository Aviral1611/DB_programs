package com.demo.employee.service;

import com.demo.employee.dao.EmployeeDAO;
import com.demo.employee.db.DatabaseConnection;
import com.demo.employee.model.Employee;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;

public class EmployeeService {
    private EmployeeDAO employeeDAO = new EmployeeDAO();

    public void printEmployeesInDepartment(int departmentId) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            List<Employee> employees = employeeDAO.getEmployeesByDepartment(conn, departmentId);
            System.out.println("Employees in Department " + departmentId + ":");
            for (Employee e : employees) {
                System.out.println(e);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void applyBonus(int departmentId, double bonusPercentage) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            employeeDAO.giveBonusToDepartment(conn, departmentId, bonusPercentage);
            System.out.println("Applied " + bonusPercentage + "% bonus to Department " + departmentId);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
