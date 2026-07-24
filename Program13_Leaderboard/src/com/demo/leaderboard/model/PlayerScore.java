package com.demo.leaderboard.model;

/**
 * Represents a player's ranking entry on the leaderboard.
 * Contains both their best score and their computed rank.
 */
public class PlayerScore {
    private String username;
    private int bestScore;
    private int rank;
    private int denseRank;
    private int totalSubmissions;

    public PlayerScore() {}

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public int getBestScore() { return bestScore; }
    public void setBestScore(int bestScore) { this.bestScore = bestScore; }

    public int getRank() { return rank; }
    public void setRank(int rank) { this.rank = rank; }

    public int getDenseRank() { return denseRank; }
    public void setDenseRank(int denseRank) { this.denseRank = denseRank; }

    public int getTotalSubmissions() { return totalSubmissions; }
    public void setTotalSubmissions(int totalSubmissions) { this.totalSubmissions = totalSubmissions; }

    @Override
    public String toString() {
        return String.format("  #%-3d (Dense: #%-3d) | %-15s | Best: %5d pts | Attempts: %d",
            rank, denseRank, username, bestScore, totalSubmissions);
    }
}
