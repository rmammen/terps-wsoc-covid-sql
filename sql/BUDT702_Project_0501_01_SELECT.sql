USE BUDT702_Project_0501_01

-- 1. Who were the top-performing players before, during, and after the COVID-19 period?
SELECT pl.playerFirstName AS 'First Name', pl.playerLastName AS 'Last Name', s.seasonYear AS 'Season',
       COUNT(p.gameId) AS 'Games Played',
       SUM(p.performanceGoalsScore) AS 'Goals',
       SUM(p.performanceAssists) AS 'Assists',
       SUM(p.performanceShots) AS 'Shots',
       (2 * SUM(p.performanceGoalsScore)) + SUM(p.performanceAssists) AS 'Points'
FROM [Wsoc.Performance] p
JOIN [Wsoc.Player] pl ON pl.playerId = p.playerId
JOIN [Wsoc.Games] g ON g.gameId = p.gameId
JOIN [Wsoc.Season] s ON s.seasonId = g.seasonId
GROUP BY pl.playerFirstName, pl.playerLastName, s.seasonYear
HAVING (2 * SUM(p.performanceGoalsScore)) + SUM(p.performanceAssists) >= 5
ORDER BY s.seasonYear, points DESC, goals DESC;

-- 2. Which opponents did Maryland have different results against across the three seasons?
SELECT  o.opponentName AS 'Opponent',
        COUNT(DISTINCT g.seasonId) AS 'Seasons Played',
        COUNT(*) AS 'Games Played',
        SUM(CASE WHEN g.gameTerpScore > g.gameOppScore THEN 1 ELSE 0 END) AS 'Wins',
        SUM(CASE WHEN g.gameTerpScore < g.gameOppScore THEN 1 ELSE 0 END) AS 'Losses',
        SUM(CASE WHEN g.gameTerpScore = g.gameOppScore THEN 1 ELSE 0 END) AS 'Ties' 
FROM    [Wsoc.Games] g
        JOIN [Wsoc.Opponent] o ON g.opponentId = o.opponentId
GROUP BY o.opponentId, o.opponentName
HAVING  COUNT(DISTINCT g.seasonId) > 1
   AND  COUNT(DISTINCT CASE WHEN g.gameTerpScore > g.gameOppScore THEN 'W'
                            WHEN g.gameTerpScore < g.gameOppScore THEN 'L'
                            ELSE 'T' END) > 1
ORDER BY o.opponentName;

-- 3. What differences can be observed in player goals, assists, shots, and minutes across the three seasons?
SELECT s.seasonYear AS 'Season Year',
    SUM(p.performanceGoalsScore) AS 'Total Goals',
    SUM(p.performanceAssists) AS 'Total Assists',
    SUM(p.performanceShots) AS 'Total Shots',
    SUM(p.performanceMinutesPlayed) AS 'Total Minutes Played'
FROM [Wsoc.Season] s
JOIN [Wsoc.Games] g
    ON s.seasonId = g.seasonId
JOIN [Wsoc.Performance] p
    ON g.gameId = p.gameId
GROUP BY
    s.seasonYear
ORDER BY
    s.seasonYear;

-- 4. When did Maryland experience its highest and lowest-scoring games during 2019–2021?
SELECT s.seasonYear AS 'Season',
       o.opponentName AS 'Opponent',
       g.gameTerpScore AS 'Maryland Score',
       g.gameOppScore AS 'Opponent Score',
       CASE WHEN g.gameTerpScore = (SELECT MAX(gameTerpScore) FROM [Wsoc.Games]) THEN 'Highest'
            ELSE 'Lowest' END AS 'Game Type'
FROM [Wsoc.Games] g
JOIN [Wsoc.Season] s ON s.seasonId = g.seasonId
JOIN [Wsoc.Opponent] o ON o.opponentId = g.opponentId
WHERE g.gameTerpScore = (SELECT MAX(gameTerpScore) FROM [Wsoc.Games])
   OR g.gameTerpScore = (SELECT MIN(gameTerpScore) FROM [Wsoc.Games])
ORDER BY g.gameTerpScore DESC, s.seasonYear;