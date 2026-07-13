package com.demo.employee.main;

import com.demo.employee.service.EmployeeService;

public class EmployeeMain {
    public static void main(String[] args) {
        System.out.println("=== Employee Management System ===");
        EmployeeService service = new EmployeeService();

        int engineeringDeptId = 2;
        System.out.println("\n[Before Bonus]");
        service.printEmployeesInDepartment(engineeringDeptId);

        service.applyBonus(engineeringDeptId, 10.0); // 10% bonus

        System.out.println("\n[After Bonus]");
        service.printEmployeesInDepartment(engineeringDeptId);
    }
}
