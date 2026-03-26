import pandas as pd


class DataParser:

    def AdditionalColumns(raceData):
        raceData = raceData.sort_values(by=["Date", "Race_ID", "Target_Rank"])

        eloBefore = []
        daysSince = []
        SB_Gap = []
        eloMomentum = []

        prevElo = {}
        prevRace = {}
        SBs = {}
        PRs = {}
        eloHistory = {}

        def ExpectedScore(elo1, elo2):
            return 1 / (1 + 10 ** ((elo2 - elo1) / 400))

        for raceId, group in raceData.groupby("Race_ID", sort=False):
            race_date = group["Date"].iloc[0]
            race_year = race_date.year
            currentSBs = {}
            athletes = group["Athlete_ID"].tolist()
            times = group["Time"].tolist()
            ranks = group["Target_Rank"].tolist()
            startingElos = {}

            for athlete in athletes:
                startingElos[athlete] = prevElo.get(athlete, 1500)
                eloBefore.append(prevElo.get(athlete, 1500))
                athleteHistory = eloHistory.get(athlete, [])
                if len(athleteHistory) >= 3:
                    eloMomentum.append(startingElos[athlete] - athleteHistory[-3])
                elif len(athleteHistory) > 0:
                    eloMomentum.append(startingElos[athlete] - athleteHistory[0])
                else:
                    eloMomentum.append(0)
                if athlete in prevRace:
                    daysSince.append((race_date - prevRace[athlete]).days)
                else:
                    daysSince.append(180)
                prevRace[athlete] = race_date
                currentSBs[athlete] = SBs.get((athlete, race_year), 999)
                athleteHistory.append(startingElos[athlete])
                eloHistory[athlete] = athleteHistory

            fastestSB = min(currentSBs.values())
            fastestPR = min(PRs.values(), default=999)

            for athlete, time in zip(athletes, times):
                athleteSB = currentSBs[athlete]
                if fastestPR == 999:
                    SB_Gap.append(0)
                elif PRs.get(athlete, 999) == 999:
                    SB_Gap.append(sum(PRs.values()) / len(PRs) - fastestPR)
                elif athleteSB == 999 or fastestSB == 999:
                    SB_Gap.append(PRs[athlete] - fastestPR)
                else:
                    SB_Gap.append(athleteSB - fastestSB)
                if time < SBs.get((athlete, race_year), 999):
                    SBs[(athlete, race_year)] = time
                if time < PRs.get(athlete, 999):
                    PRs[athlete] = time

            eloDeltas = {athlete: 0 for athlete in athletes}
            k = 43
            if len(eloHistory[athlete]) > 5:
                k = 30
            for i in range(len(athletes)):
                for j in range(i + 1, len(athletes)):
                    athlete1Elo = startingElos.get(athletes[i], 1500)
                    athlete2Elo = startingElos.get(athletes[j], 1500)
                    if ranks[i] < ranks[j]:
                        eloDeltas[athletes[i]] += k * (
                            1 - ExpectedScore(athlete1Elo, athlete2Elo)
                        )
                        eloDeltas[athletes[j]] += k * (
                            0 - ExpectedScore(athlete2Elo, athlete1Elo)
                        )
                    elif ranks[i] > ranks[j]:
                        eloDeltas[athletes[i]] += k * (
                            0 - ExpectedScore(athlete1Elo, athlete2Elo)
                        )
                        eloDeltas[athletes[j]] += k * (
                            1 - ExpectedScore(athlete2Elo, athlete1Elo)
                        )
            for athlete in athletes:
                prevElo[athlete] = startingElos[athlete] + (eloDeltas[athlete])

        raceData["Elo_Before"] = eloBefore
        raceData["Days_since_last"] = daysSince
        raceData["SB_Gap"] = SB_Gap
        raceData["Elo_Momentum"] = eloMomentum
        return raceData
