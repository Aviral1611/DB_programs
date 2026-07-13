package com.demo.employee.model;

public class Employee {
    private int employeeId;
    private String name;
    private double salary;
    private int departmentId;

    public Employee(int employeeId, String name, double salary, int departmentId) {
        this.employeeId = employeeId;
        this.name = name;
        this.salary = salary;
        this.departmentId = departmentId;
    }

    @Override
    public String toString() {
        return "Employee [ID=" + employeeId + ", Name=" + name + ", Salary=$" + salary + ", DeptID=" + departmentId + "]";
    }
}
