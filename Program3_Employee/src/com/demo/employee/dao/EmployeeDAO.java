package com.demo.employee.dao;

import com.demo.employee.model.Employee;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class EmployeeDAO {
    public List<Employee> getEmployeesByDepartment(Connection conn, int departmentId) throws SQLException {
        List<Employee> employees = new ArrayList<>();
        String sql = "SELECT * FROM employees WHERE department_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, departmentId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    employees.add(new Employee(
                        rs.getInt("employee_id"),
                        rs.getString("name"),
                        rs.getDouble("salary"),
                        rs.getInt("department_id")
                    ));
                }
            }
        }
        return employees;
    }

    public void giveBonusToDepartment(Connection conn, int departmentId, double bonusPercentage) throws SQLException {
        String sql = "UPDATE employees SET salary = salary + (salary * ?) WHERE department_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setDouble(1, bonusPercentage / 100.0);
            pstmt.setInt(2, departmentId);
            pstmt.executeUpdate();
        }
    }
}
