package com.demo.leaderboard.main;

import com.demo.leaderboard.service.LeaderboardService;
import com.demo.leaderboard.util.ConfigLoader;

public class LeaderboardMain {
    public static void main(String[] args) {
        System.out.println("=== Gaming Leaderboard (Window Functions) ===\n");

        ConfigLoader.load();
        LeaderboardService service = new LeaderboardService();
        service.clearData();

        // 1. Register players
        System.out.println("[Step 1] Registering players...");
        int p1 = service.registerPlayer("ShadowNinja");
        int p2 = service.registerPlayer("DragonSlayer");
        int p3 = service.registerPlayer("PixelQueen");
        int p4 = service.registerPlayer("CodeWizard");
        int p5 = service.registerPlayer("StormBreaker");

        // 2. Submit multiple scores per player (simulating multiple game rounds)
        System.out.println("\n[Step 2] Playing rounds and submitting scores...");

        // ShadowNinja plays 3 rounds, improving each time
        service.submitScore(p1, "ShadowNinja", 720);
        service.submitScore(p1, "ShadowNinja", 850);
        service.submitScore(p1, "ShadowNinja", 940);

        // DragonSlayer plays 2 rounds
        service.submitScore(p2, "DragonSlayer", 880);
        service.submitScore(p2, "DragonSlayer", 760);

        // PixelQueen plays 4 rounds — scores a tie with ShadowNinja's best!
        service.submitScore(p3, "PixelQueen", 600);
        service.submitScore(p3, "PixelQueen", 710);
        service.submitScore(p3, "PixelQueen", 940);  // TIE with ShadowNinja!
        service.submitScore(p3, "PixelQueen", 800);

        // CodeWizard plays 1 round
        service.submitScore(p4, "CodeWizard", 990);

        // StormBreaker plays 2 rounds
        service.submitScore(p5, "StormBreaker", 850);
        service.submitScore(p5, "StormBreaker", 830);

        // 3. Display the live leaderboard
        service.displayLeaderboard();

        // 4. Show individual player history
        System.out.println("\n[Step 4] Player Deep Dive...");
        service.showPlayerHistory("ShadowNinja");
        service.showPlayerHistory("PixelQueen");
    }
}
