package com.demo.bank.main;

import com.demo.bank.service.BankService;

public class BankMain {
    public static void main(String[] args) {
        System.out.println("--- Bank Transaction Manager ---");
        BankService bankService = new BankService();

        int aliceId = 1;
        int bobId = 2;

        System.out.println("\n[Before Transfer]");
        bankService.printAccountDetails(aliceId);
        bankService.printAccountDetails(bobId);

        System.out.println("\n[Initiating Transfer: Alice to Bob - $500]");
        boolean success = bankService.transferFunds(aliceId, bobId, 500.0);

        if (success) {
            System.out.println("\n[After Successful Transfer]");
            bankService.printAccountDetails(aliceId);
            bankService.printAccountDetails(bobId);
        }

        System.out.println("\n[Initiating Failing Transfer: Bob to Alice - $10000 (Insufficient Funds)]");
        bankService.transferFunds(bobId, aliceId, 10000.0);
        
        System.out.println("\n[After Failed Transfer (Values should remain unchanged)]");
        bankService.printAccountDetails(aliceId);
        bankService.printAccountDetails(bobId);
    }
}
