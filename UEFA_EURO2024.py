from ortools.sat.python import cp_model
import random

class TournamentData:
    def __init__(self):
        # Initialisation des équipes et des chapeaux
        self.teams = [
            "Germany", "England", "Albania", "Austria", "Belgium", "Croatia", "Denmark",
            "Scotland", "Spain", "France", "Georgia", "Hungary", "Italy", "Netherlands",
            "Portugal", "Poland", "Czech Republic", "Romania", "Serbia", "Ukraine",
            "Slovakia", "Slovenia", "Switzerland", "Turkey"
        ]
        self.chapeaus = {
            'Chapeau_1': ["Germany", "Portugal", "France", "Spain", "Belgium", "England"],
            'Chapeau_2': ["Hungary", "Turkey", "Romania", "Denmark", "Albania", "Austria"],
            'Chapeau_3': ["Netherlands", "Scotland", "Croatia", "Slovenia", "Slovakia", "Czech Republic"],
            'Chapeau_4': ["Italy", "Serbia", "Switzerland", "Poland", "Ukraine", "Georgia"]
        }
        self.groups = {
            'group_A': [],
            'group_B': [],
            'group_C': [],
            'group_D': [],
            'group_E': [],
            'group_F': []
        }
        # Initialisation des stades, créneaux horaires et jours
        self.stadiums = [
            "Olympiastadion", "RheinEnergieStadion", "Signal_Iduna_Park", "Merkur_Spiel_Arena",
            "Deutsche_Bank_Park", "Volksparkstadion", "Allianz_Arena", "MHPArena",
            "Red_Bull_Arena", "Veltins_Arena"
        ]
        self.time_slots = ["3pm", "6pm", "9pm"]
        self.days = [
            "Friday_14_06", "Saturday_15_06", "Sunday_16_06", "Monday_17_06",
            "Tuesday_18_06", "Wednesday_19_06", "Thursday_20_06", "Friday_21_06",
            "Saturday_22_06", "Sunday_23_06", "Monday_24_06", "Tuesday_25_06",
            "Wednesday_26_06"
        ]
        self.phase = ["group_journey_1", "group_journey_2", "group_journey_3"]
        self.group_matches = {
            'group_A': [],
            'group_B': [],
            'group_C': [],
            'group_D': [],
            'group_E': [],
            'group_F': []
        }

class MyModel:
    def __init__(self, data):
        self.data = data
        self.model = cp_model.CpModel()
        self.team_group_vars = {}
        self.match_vars = {}
        self.group_ids = list(self.data.groups.keys())
        self.generated_matches = {}

    def setup_model(self):
        # Variables d'affectation des équipes aux groupes
        for team in self.data.teams:
            for group_id in range(len(self.group_ids)):
                var_name = f"{team}_in_{self.group_ids[group_id]}"
                self.team_group_vars[(team, group_id)] = self.model.NewBoolVar(var_name)

        # Contraintes : L'Allemagne dans le groupe A
        self.model.Add(self.team_group_vars[("Germany", 0)] == 1)  # group_A est 0

        # Chaque équipe dans exactement un groupe
        for team in self.data.teams:
            self.model.Add(sum(self.team_group_vars[(team, i)] for i in range(len(self.group_ids))) == 1)

        # Une équipe au maximum par chapeau dans un groupe
        for i, group_name in enumerate(self.group_ids):
            for chapeau, teams in self.data.chapeaus.items():
                team_vars_in_chapeau = [self.team_group_vars[(team, i)] for team in teams]
                self.model.AddAtMostOne(team_vars_in_chapeau)

    def solve(self):
        # Résolution du modèle
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            groups = {group_name: [] for group_name in self.group_ids}
            for team in self.data.teams:
                for i, group_name in enumerate(self.group_ids):
                    if solver.Value(self.team_group_vars[(team, i)]):
                        groups[group_name].append(team)
            return groups
        else:
            print("No feasible solution found.")
            return None

    def setup_model_journey(self, group):
        # Initialisation du modèle pour un groupe
        self.model_journey = cp_model.CpModel()
        self.matches = []
        num_teams = len(group)
        num_phases = 3

        # Variables : match[i][j][p] est True si l'équipe i joue contre l'équipe j dans la phase p
        self.match_vars = {}
        for i in range(num_teams):
            for j in range(i + 1, num_teams):
                for p in range(num_phases):
                    var = self.model_journey.NewBoolVar(f'match_{group[i]}_{group[j]}_phase_{p}')
                    self.match_vars[(group[i], group[j], p)] = var

        # Chaque équipe joue contre chaque autre équipe exactement une fois dans toutes les phases
        for i in range(num_teams):
            for j in range(i + 1, num_teams):
                self.model_journey.Add(sum(self.match_vars[(group[i], group[j], p)] for p in range(num_phases)) == 1)

        # Chaque équipe joue un match par phase
        for p in range(num_phases):
            for i in range(num_teams):
                self.model_journey.Add(sum(self.match_vars[(group[i], group[j], p)]
                                           if (group[i], group[j], p) in self.match_vars else self.match_vars[
                    (group[j], group[i], p)]
                                           for j in range(num_teams) if i != j) == 1)

    def solve_model_journey(self):
        # Résolution du modèle de phase de groupe
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model_journey)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            phases = {1: [], 2: [], 3: []}
            for (team1, team2, p), var in self.match_vars.items():
                if solver.Value(var):
                    phases[p + 1].append((team1, team2))
            return phases
        else:
            print("No feasible solution found.")
            return None

    def setup_model2(self, groups):
        self.matches_journey_1 = []
        self.matches_journey_2 = []
        self.matches_journey_3 = []

        self.generated_matches = {}

        # Générer tous les matchs une fois et les stocker en utilisant le modèle de contrainte
        for group_name, teams in groups.items():
            self.setup_model_journey(teams)
            group_phases = self.solve_model_journey()
            if group_phases:
                self.generated_matches[group_name] = group_phases
            else:
                print(f"Failed to create matches for {group_name}")
                return

        # Premier match de la phase 1
        opening_match_opponent = None
        for match in self.generated_matches["group_A"][1]:
            if "Germany" in match:
                opening_match_opponent = match[1] if match[0] == "Germany" else match[0]
                break

        opening_match = ("Germany", opening_match_opponent, "Friday_14_06", "9pm", "Allianz_Arena")
        self.matches_journey_1.append(opening_match)

        # Retirer le match d'ouverture des matchs de la phase 1 du groupe A
        self.generated_matches["group_A"][1] = [match for match in self.generated_matches["group_A"][1] if
                                                "Germany" not in match]

        # Commencer la planification pour la phase 1 à partir du deuxième jour
        time_index = 0
        days = self.data.days[1:]
        used_stadiums = {day: [] for day in days}  # Suivre les stades utilisés chaque jour

        # Planifier les matchs dans l'ordre des groupes pour la phase 1
        for group_name in self.group_ids:
            matches = self.generated_matches[group_name][1]  # matchs de la phase 1
            for match in matches:
                day = days[time_index // len(self.data.time_slots)]
                time_slot = self.data.time_slots[time_index % len(self.data.time_slots)]

                # Sélectionner un stade non utilisé ce jour-là
                available_stadiums = [stadium for stadium in self.data.stadiums if stadium not in used_stadiums[day]]
                if not available_stadiums:
                    continue  # Si aucun stade disponible, passer à la prochaine combinaison
                stadium = random.choice(available_stadiums)
                used_stadiums[day].append(stadium)

                match_var = (match[0], match[1], day, time_slot, stadium)
                self.matches_journey_1.append(match_var)

                time_index += 1

        # Assurer l'absence de doublons pour la phase 1
        used_teams = set()
        final_matches = []
        for match in self.matches_journey_1:
            if (match[0], match[1]) not in used_teams and (match[1], match[0]) not in used_teams:
                final_matches.append(match)
                used_teams.add((match[0], match[1]))
                used_teams.add((match[1], match[0]))

        self.matches_journey_1 = final_matches

        # Commencer la planification pour la phase 2
        time_index = 0
        days = self.data.days[5:]  # Commencer à partir de Tuesday_18_06
        used_stadiums = {day: [] for day in days}  # Suivre les stades utilisés chaque jour

        for group_name in self.group_ids:
            matches = self.generated_matches[group_name][2]  # matchs de la phase 2
            used_teams = set()
            for match in matches:
                if match[0] in used_teams or match[1] in used_teams:
                    continue

                day = days[time_index // len(self.data.time_slots)]
                time_slot = self.data.time_slots[time_index % len(self.data.time_slots)]

                # Sélectionner un stade non utilisé ce jour-là
                available_stadiums = [stadium for stadium in self.data.stadiums if stadium not in used_stadiums[day]]
                if not available_stadiums:
                    continue  # Si aucun stade disponible, passer à la prochaine combinaison
                stadium = random.choice(available_stadiums)
                used_stadiums[day].append(stadium)

                match_var = (match[0], match[1], day, time_slot, stadium)
                self.matches_journey_2.append(match_var)

                time_index += 1
                used_teams.add(match[0])
                used_teams.add(match[1])

        # Assurer l'absence de doublons pour la phase 2
        used_teams = set()
        final_matches = []
        for match in self.matches_journey_2:
            if (match[0], match[1]) not in used_teams and (match[1], match[0]) not in used_teams:
                final_matches.append(match)
                used_teams.add((match[0], match[1]))
                used_teams.add((match[1], match[0]))

        self.matches_journey_2 = final_matches

        # Commencer la planification pour la phase 3
        time_index = 0
        days = self.data.days[9:]  # Commencer à partir de Sunday_23_06
        used_stadiums = {day: [] for day in days}  # Suivre les stades utilisés chaque jour

        for group_name in self.group_ids:
            matches = self.generated_matches[group_name][3]  # matchs de la phase 3
            used_teams = set()
            for match in matches:
                if match[0] in used_teams or match[1] in used_teams:
                    continue

                day = days[time_index // 2]
                time_slot = "6pm" if time_index % 2 == 0 else "9pm"

                # Sélectionner un stade non utilisé ce jour-là
                available_stadiums = [stadium for stadium in self.data.stadiums if stadium not in used_stadiums[day]]
                if not available_stadiums:
                    continue  # Si aucun stade disponible, passer à la prochaine combinaison
                stadium = random.choice(available_stadiums)
                used_stadiums[day].append(stadium)

                match_var = (match[0], match[1], day, time_slot, stadium)
                self.matches_journey_3.append(match_var)

                used_teams.add(match[0])
                used_teams.add(match[1])

            time_index += 1  # Augmenter l'index de temps uniquement après avoir planifié deux matchs pour chaque groupe

        # Assurer l'absence de doublons pour la phase 3
        used_teams = set()
        final_matches = []
        for match in self.matches_journey_3:
            if (match[0], match[1]) not in used_teams and (match[1], match[0]) not in used_teams:
                final_matches.append(match)
                used_teams.add((match[0], match[1]))
                used_teams.add((match[1], match[0]))

        self.matches_journey_3 = final_matches

    def solve2(self):
        # Résolution du modèle global
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self.matches_journey_1, self.matches_journey_2, self.matches_journey_3
        else:
            print("No feasible solution found.")
            return None, None, None

    def display_schedule(self, journey_1, journey_2, journey_3, knockout_matches):
        # Affichage des calendriers des phases de groupes
        print("========Let's make the calendar !========")
        print("group_journey_1 :")
        match_count = 1
        for group_name in self.group_ids:
            print(f"{group_name}")
            group_matches = [match for match in journey_1 if
                             match[0] in self.data.groups[group_name] or match[1] in self.data.groups[group_name]]
            for match in group_matches:
                print(f"Match {match_count}: {match[0]} vs {match[1]} - {match[2]} - {match[3]} - {match[4]}")
                match_count += 1

        print("\ngroup_journey_2 :")
        for group_name in self.group_ids:
            print(f"{group_name}")
            group_matches = [match for match in journey_2 if
                             match[0] in self.data.groups[group_name] or match[1] in self.data.groups[group_name]]
            for match in group_matches:
                print(f"Match {match_count}: {match[0]} vs {match[1]} - {match[2]} - {match[3]} - {match[4]}")
                match_count += 1

        print("\ngroup_journey_3 :")
        for group_name in self.group_ids:
            print(f"{group_name}")
            group_matches = [match for match in journey_3 if
                             match[0] in self.data.groups[group_name] or match[1] in self.data.groups[group_name]]
            for match in group_matches:
                print(f"Match {match_count}: {match[0]} vs {match[1]} - {match[2]} - {match[3]} - {match[4]}")
                match_count += 1

        # Affichage des matchs de la phase finale avec des titres
        print("\n========knockout phase !========")

        # Regrouper les matchs par phase
        knockout_phases = {'round_of_16': [], 'quarter_final': [], 'semi_final': [], 'final': []}
        for match in knockout_matches:
            knockout_phases[match['phase']].append(match)

        # Afficher chaque phase
        for phase, matches in knockout_phases.items():
            print(f"\n{phase.replace('_', ' ')} :")
            for match in matches:
                print(f"Match {match['match_id']}: {match['team1']} - {match['team2']} - {match['day']} - {match['time_slot']} - {match['stade']}")

    def schedule_semi_final(self, euro_data):
        # Planification des demi-finales
        match_id = 49  # Début des ID de match pour la phase des demi-finales
        days = ['Tuesday_09_07', 'Wednesday_10_07']  # Jours alloués aux demi-finales
        time_slot = '9pm'  # Tous les matchs des demi-finales se jouent à 9pm
        matches = []

        # Simuler les matchs basés sur les hypothétiques vainqueurs des quarts de finale
        matchups = [
            ('W45', 'W46'),  # Vainqueurs des matchs des quarts de finale 45 et 46
            ('W47', 'W48')  # Vainqueurs des matchs des quarts de finale 47 et 48
        ]

        used_stadiums = {day: [] for day in days}  # Suivre les stades utilisés chaque jour

        # Assigner les matchs sur deux jours
        for i, matchup in enumerate(matchups):
            day = days[i]
            # Sélectionner un stade non utilisé ce jour-là
            available_stadiums = [stadium for stadium in euro_data.stadiums if stadium not in used_stadiums[day]]
            if not available_stadiums:
                continue  # Si aucun stade disponible, passer à la prochaine combinaison
            stadium = random.choice(available_stadiums)
            used_stadiums[day].append(stadium)

            matches.append({
                'match_id': match_id,
                'phase': 'semi_final',
                'day': day,
                'time_slot': time_slot,
                'team1': matchup[0],
                # Les équipes ici sont hypothétiques et devraient être déterminées par les résultats réels
                'team2': matchup[1],
                'stade': stadium
            })
            match_id += 1

        return matches

    def schedule_knockout_phase(self, euro_data):
        # Planification des phases finales
        matches = self.schedule_round_of_16(euro_data)
        quarter_final_matches = self.schedule_quarter_final(euro_data)
        semi_final_matches = self.schedule_semi_final(euro_data)
        final_match = self.schedule_final(euro_data)
        matches.extend(quarter_final_matches)
        matches.extend(semi_final_matches)
        matches.extend(final_match)
        return matches

    def schedule_final(self, euro_data):
        # Planification de la finale
        match_id = 51  # ID du match pour la finale
        day = 'Sunday_14_07'  # Jour alloué à la finale
        time_slot = '9pm'  # Heure du match
        stadium = 'Olympiastadion'  # Stade choisi pour la finale

        # Simuler les équipes basées sur les vainqueurs hypothétiques des demi-finales
        team1 = 'W49'  # Vainqueur du match 49 des demi-finales
        team2 = 'W50'  # Vainqueur du match 50 des demi-finales

        # Création du match de la finale
        final_match = {
            'match_id': match_id,
            'phase': 'final',
            'day': day,
            'time_slot': time_slot,
            'team1': team1,
            'team2': team2,
            'stade': stadium
        }

        return [final_match]  # Retourner une liste contenant uniquement le match de la finale

    def schedule_round_of_16(self, euro_data):
        # Planification des huitièmes de finale
        match_id = 37  # Début des ID de match pour la phase round_of_16
        days = ['Saturday_29_06', 'Sunday_30_06', 'Monday_01_07', 'Tuesday_02_07']  # Jours alloués à la round_of_16
        time_slots = ['6pm', '9pm']  # Créneaux horaires pour les matchs
        matches = []

        # Planification hypothétique des matchs basée sur des désignations fictives pour les équipes
        matchups = [
            ('1A', '2C'), ('2A', '2B'), ('1B', '3A/D/E/F'), ('1C', '3D/E/F'),
            ('1F', '3A/B/C'), ('2D', '2E'), ('1E', '3A/B/C/D'), ('1D', '2F')
        ]

        used_stadiums = {day: [] for day in days}  # Suivre les stades utilisés chaque jour

        # Assigner les matchs sur 4 jours avec 2 matchs par jour
        for i, matchup in enumerate(matchups):
            day = days[i // 2]
            time_slot = time_slots[i % 2]

            # Sélectionner un stade non utilisé ce jour-là
            available_stadiums = [stadium for stadium in euro_data.stadiums if stadium not in used_stadiums[day]]
            if not available_stadiums:
                continue  # Si aucun stade disponible, passer à la prochaine combinaison
            stadium = random.choice(available_stadiums)
            used_stadiums[day].append(stadium)

            matches.append({
                'match_id': match_id,
                'phase': 'round_of_16',
                'day': day,
                'time_slot': time_slot,
                'team1': matchup[0],  # Les équipes ici sont hypothétiques et devraient être remplacées
                'team2': matchup[1],
                'stade': stadium
            })
            match_id += 1

        return matches

    def schedule_quarter_final(self, euro_data):
        # Planification des quarts de finale
        match_id = 45  # Début des ID de match pour la phase des quarts de finale
        days = ['Friday_05_07', 'Saturday_06_07']  # Jours alloués aux quarts de finale
        time_slots = ['6pm', '9pm']  # Créneaux horaires pour les matchs
        matches = []

        # Simuler les matchs basés sur les hypothétiques vainqueurs des huitièmes de finale
        matchups = [
            ('W39', 'W37'), ('W41', 'W42'), ('W43', 'W44'), ('W40', 'W38')
        ]

        used_stadiums = {day: [] for day in days}  # Suivre les stades utilisés chaque jour

        # Assigner les matchs sur deux jours avec deux matchs par jour
        for i, matchup in enumerate(matchups):
            day = days[i // 2]
            time_slot = time_slots[i % 2]

            # Sélectionner un stade non utilisé ce jour-là
            available_stadiums = [stadium for stadium in euro_data.stadiums if stadium not in used_stadiums[day]]
            if not available_stadiums:
                continue  # Si aucun stade disponible, passer à la prochaine combinaison
            stadium = random.choice(available_stadiums)
            used_stadiums[day].append(stadium)

            matches.append({
                'match_id': match_id,
                'phase': 'quarter_final',
                'day': day,
                'time_slot': time_slot,
                'team1': matchup[0],
                # Les équipes ici sont hypothétiques et devraient être déterminées par les résultats réels
                'team2': matchup[1],
                'stade': stadium
            })
            match_id += 1

        return matches

def main():
    data = TournamentData()
    print(data.chapeaus['Chapeau_1'])
    print(data.chapeaus['Chapeau_2'])
    print(data.chapeaus['Chapeau_3'])
    print(data.chapeaus['Chapeau_4'])
    model = MyModel(data)
    model.setup_model()
    groups = model.solve()
    if groups:
        print("========Let's draw groups !========")
        for group_name, teams in groups.items():
            print(f"{group_name}: {teams}")
            data.groups[group_name] = teams  # Sauvegarder les groupes pour les utiliser plus tard dans la planification

        model.setup_model2(groups)
        journey_1, journey_2, journey_3 = model.solve2()
        if journey_1 and journey_2 and journey_3:
            knockout_matches = model.schedule_knockout_phase(data)
            model.display_schedule(journey_1, journey_2, journey_3, knockout_matches)
        else:
            print("Failed to create schedule.")
    else:
        print("Failed to draw groups, cannot schedule matches.")

if __name__ == "__main__":
    main()
