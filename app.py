import customtkinter as ctk
from tkinter import messagebox
from config import load_config, save_config
from jira_api import JiraAPI
import threading
import urllib.request
import json

APP_VERSION = "1.3.0"
GITHUB_RELEASES_URL = "https://api.github.com/repos/DavyLss/jira-us-creator/releases/latest"
GITHUB_RELEASES_PAGE = "https://github.com/DavyLss/jira-us-creator/releases/latest"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class JiraConfigFrame(ctk.CTkFrame):
    def __init__(self, master, config, on_saved=None):
        super().__init__(master)
        self.config = config
        self.on_saved = on_saved
        self.jira = None
        self._build()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Configuration Jira",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=20, pady=20, sticky="w")

        ctk.CTkLabel(self, text="URL Jira:").grid(
            row=1, column=0, padx=20, pady=8, sticky="w")
        self.url_entry = ctk.CTkEntry(self, width=400)
        self.url_entry.insert(0, self.config.get("jira_url", ""))
        self.url_entry.grid(row=1, column=1, padx=10, pady=8, sticky="we")
        ctk.CTkLabel(self, text="(ex: https://jira.votre-entreprise.fr/jira)",
                     text_color="gray").grid(row=1, column=2, padx=5, sticky="w")

        ctk.CTkLabel(self, text="Token / Jeton personnel:").grid(
            row=2, column=0, padx=20, pady=8, sticky="w")
        self.token_entry = ctk.CTkEntry(self, width=400, show="*")
        self.token_entry.insert(0, self.config.get("jira_token", ""))
        self.token_entry.grid(row=2, column=1, padx=10, pady=8, sticky="we")
        self.show_token_btn = ctk.CTkButton(
            self, text="Afficher", width=80,
            command=self._toggle_token)
        self.show_token_btn.grid(row=2, column=2, padx=5, sticky="w")

        self.ssl_var = ctk.BooleanVar(
            value=self.config.get("verify_ssl", True))
        ctk.CTkCheckBox(self, text="Vérifier le certificat SSL",
                        variable=self.ssl_var).grid(
            row=3, column=0, columnspan=2, padx=20, pady=8, sticky="w")

        self.test_btn = ctk.CTkButton(
            self, text="Tester la connexion",
            command=self._test_connection)
        self.test_btn.grid(row=4, column=0, columnspan=3, padx=20, pady=10)

        self.status_lbl = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_lbl.grid(row=5, column=0, columnspan=3, padx=20, pady=5)

        self.update_btn = ctk.CTkButton(
            self, text="Vérifier les mises à jour", width=180,
            command=lambda: check_for_updates(self),
            fg_color="#5b8af5", hover_color="#3a6fd4")
        self.update_btn.grid(row=6, column=0, columnspan=3, padx=20, pady=5)

        self.auto_save_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="Sauvegarde automatique",
                        variable=self.auto_save_var).grid(
            row=7, column=0, columnspan=3, padx=20, pady=5, sticky="w")

        self.uninstall_btn = ctk.CTkButton(
            self, text="Désinstaller", width=120,
            command=self._uninstall,
            fg_color="#c0392b", hover_color="#e74c3c")
        self.uninstall_btn.grid(row=8, column=0, columnspan=3, padx=20, pady=10)

    def _toggle_token(self):
        show = self.token_entry.cget("show") == ""
        self.token_entry.configure(show="*" if show else "")

    def _test_connection(self):
        url = self.url_entry.get().strip()
        token = self.token_entry.get().strip()
        if not all([url, token]):
            self.status_lbl.configure(text_color="red")
            self.status_lbl.configure(text="Veuillez remplir l'URL et le token")
            return
        self.test_btn.configure(state="disabled", text="Test en cours...")
        self.status_lbl.configure(text_color="blue")
        self.status_lbl.configure(text="Connexion en cours...")
        threading.Thread(target=self._do_test,
                         args=(url, token), daemon=True).start()

    def _do_test(self, url, token):
        api = JiraAPI(url, token, self.ssl_var.get())
        ok, name, info = api.test_connection()
        self.after(0, self._test_done, ok, name, info)

    def _test_done(self, ok, name, info):
        self.test_btn.configure(state="normal", text="Tester la connexion")
        if ok:
            self.jira = JiraAPI(self.url_entry.get().strip(),
                                self.token_entry.get().strip(),
                                self.ssl_var.get())
            self.config["jira_url"] = self.url_entry.get().strip()
            self.config["jira_token"] = self.token_entry.get().strip()
            self.config["verify_ssl"] = self.ssl_var.get()
            save_config(self.config)
            self.status_lbl.configure(text_color="green")
            self.status_lbl.configure(text=f"Connecté en tant que {name}")
            self._load_all_projects()
        else:
            self.jira = None
            self.status_lbl.configure(text_color="red")
            self.status_lbl.configure(text=f"Échec: {info}")

    def _load_all_projects(self):
        if self.jira:
            threading.Thread(target=self._do_load_projects, daemon=True).start()

    def _do_load_projects(self):
        try:
            projects = self.jira.get_projects()
            if projects:
                self.after(0, self._projects_loaded, projects)
        except Exception:
            pass

    def _projects_loaded(self, projects):
        n = len(projects)
        self.status_lbl.configure(text=f"{n} projet(s) chargé(s)", text_color="green")

    def _uninstall(self):
        import sys
        import subprocess
        from tkinter import messagebox
        if messagebox.askyesno("Désinstaller", "Voulez-vous vraiment désinstaller Jira US Creator ?\n\nCela supprimera le raccourci bureau et les données locales."):
            root = self.winfo_toplevel()
            root.destroy()
            subprocess.Popen([sys.executable, "--uninstall"])


class UpdateCheckPopup(ctk.CTkToplevel):
    def __init__(self, master, current_version, latest_version, download_url, notes=""):
        super().__init__(master)
        self.title("Mise à jour disponible")
        self.geometry("450x350")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._build(current_version, latest_version, download_url, notes)
        self.lift()
        self.focus_force()

    def _build(self, current_version, latest_version, download_url, notes):
        ctk.CTkLabel(self, text="Nouvelle version disponible",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#4ade80").pack(pady=(20, 5))

        ctk.CTkLabel(self, text=f"Version actuelle : {current_version}",
                     text_color="gray").pack(pady=2)
        ctk.CTkLabel(self, text=f"Dernière version : {latest_version}",
                     text_color="#4ade80",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=2)

        if notes:
            ctk.CTkTextbox(self, height=120, width=380, state="normal",
                           corner_radius=8).pack(padx=20, pady=15, fill="x")
            txt = self.nametowidget(self.winfo_children()[-2].winfo_name()) if hasattr(self.nametowidget(self.winfo_children()[-2].winfo_name()), 'insert') else None
            tb = self.winfo_children()[-1]
            tb.configure(state="normal")
            tb.insert("1.0", notes)
            tb.configure(state="disabled")

        ctk.CTkButton(
            self, text="Télécharger", fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000", font=ctk.CTkFont(weight="bold"),
            command=lambda: self._open_url(download_url)).pack(pady=10)
        ctk.CTkButton(
            self, text="Plus tard", text_color="gray",
            fg_color="transparent", hover_color="gray",
            command=self.destroy).pack()

def _newer_version(latest, current):
    def _parse(v):
        return [int(x) for x in v.split(".")]
    return _parse(latest) > _parse(current)


class HelpInfoPopup(ctk.CTkToplevel):
    def __init__(self, master, title, message):
        super().__init__(master)
        self.title(title)
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._build(message)
        self.lift()
        self.focus_force()

    def _build(self, message):
        ctk.CTkLabel(self, text=message, wraplength=350, justify="left").pack(
            padx=20, pady=15, fill="both", expand=True)
        ctk.CTkButton(self, text="Fermer", command=self.destroy).pack(pady=10)


class SPEstimatorPopup(ctk.CTkToplevel):
    def __init__(self, master, on_result=None):
        super().__init__(master)
        self.title("Estimateur Story Points")
        self.geometry("500x520")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.on_result = on_result
        self.calculated_sp = None
        self._build()
        self.lift()
        self.focus_force()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Aide pour estimer ma Jira..",
                     font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=20, pady=15, sticky="w")

        # --- Temps estimé ---
        ctk.CTkLabel(self, text="1. Temps estimé:").grid(
            row=1, column=0, padx=20, pady=8, sticky="w")
        self.time_var = ctk.StringVar()
        f = ctk.CTkFrame(self)
        f.grid(row=1, column=1, padx=20, pady=8, sticky="w")
        self.time_combo = ctk.CTkComboBox(
            f, width=200, variable=self.time_var, state="readonly",
            values=["< 2h", "< 3h30", "< 14h (2j)", "< 28h (4j)", "≤ 35h (5j)", "> 35h"])
        self.time_combo.pack(side="left")
        ctk.CTkButton(
            f, text="💡", width=24, height=24,
            command=lambda: HelpInfoPopup(
                self, "Temps estimé",
                "Combien de temps cela va-t-il prendre sans interruption ?\n\n"
                "• < 2h      → Tâche rapide, script simple\n"
                "• < 3h30    → Demi-journée, configuration légère\n"
                "• < 14h (2j)→ 2 jours, développement modéré\n"
                "• < 28h (4j)→ 4 jours, fonctionnalité complexe\n"
                "• ≤ 35h (5j)→ Semaine complète, gros chantier\n"
                "• > 35h     → Nécessiterait plusieurs sprints\n\n"
                "Posez-vous la question : si je devais le faire en\n"
                "une seule session, combien d'heures faudrait-il ?"),
            fg_color="#5b8af5", hover_color="#3a6fd4").pack(side="left", padx=(4, 0))

        # --- Connaissance ---
        ctk.CTkLabel(self, text="2. Connaissance:").grid(
            row=2, column=0, padx=20, pady=8, sticky="w")
        self.know_var = ctk.StringVar()
        f = ctk.CTkFrame(self)
        f.grid(row=2, column=1, padx=20, pady=8, sticky="w")
        self.know_combo = ctk.CTkComboBox(
            f, width=200, variable=self.know_var, state="readonly",
            values=["Tout", "Presque tout", "Quelque chose", "Presque rien", "Rien / inconnue"])
        self.know_combo.pack(side="left")
        ctk.CTkButton(
            f, text="💡", width=24, height=24,
            command=lambda: HelpInfoPopup(
                self, "Connaissance",
                "Quel est mon niveau de maîtrise sur ce sujet ?\n\n"
                "• Tout        → Je maîtrise, déjà fait plusieurs fois\n"
                "• Presque tout→ Bonne maîtrise, quelques vérifications\n"
                "• Quelque ch. → Vu ou fait mais pas régulièrement\n"
                "• Presque rien→ Peu de compétence, besoin d'aide\n"
                "• Rien/inconnue→ Zéro expérience sur le sujet\n\n"
                "Être honnête ici évite de sous-estimer le travail\n"
                "sur des sujets non familiers."),
            fg_color="#5b8af5", hover_color="#3a6fd4").pack(side="left", padx=(4, 0))

        # --- Dépendances ---
        ctk.CTkLabel(self, text="3. Dépendances:").grid(
            row=3, column=0, padx=20, pady=8, sticky="w")
        self.dep_var = ctk.StringVar()
        f = ctk.CTkFrame(self)
        f.grid(row=3, column=1, padx=20, pady=8, sticky="w")
        self.dep_combo = ctk.CTkComboBox(
            f, width=200, variable=self.dep_var, state="readonly",
            values=["Aucune", "Presque aucune", "Quelques (≥ 3)", "Peu (≥ 4)", "Plus que peu (≥ 5)", "Inconnue (?)"])
        self.dep_combo.pack(side="left")
        ctk.CTkButton(
            f, text="💡", width=24, height=24,
            command=lambda: HelpInfoPopup(
                self, "Dépendances",
                "Combien de dépendances externes ai-je ?\n\n"
                "• Aucune    → Autonomie totale\n"
                "• Presque auc. → Un échange rapide suffit\n"
                "• Quelques (≥3)→ Plusieurs validations / équipes\n"
                "• Peu (≥4)  → Attente ressources, accès, environnements\n"
                "• Plus que peu(≥5)→ Forte dépendance, inconnues\n"
                "• Inconnue  → Non identifiable à ce stade\n\n"
                "Les dépendances créent du temps d'attente et\n"
                "d'incertitude. Comptez tout blocage externe."),
            fg_color="#5b8af5", hover_color="#3a6fd4").pack(side="left", padx=(4, 0))

        # --- Nb applications ---
        ctk.CTkLabel(self, text="4. Nb applications:").grid(
            row=4, column=0, padx=20, pady=8, sticky="w")
        self.apps_var = ctk.StringVar(value="1")
        f = ctk.CTkFrame(self)
        f.grid(row=4, column=1, padx=20, pady=8, sticky="w")
        self.apps_entry = ctk.CTkEntry(f, width=80, textvariable=self.apps_var)
        self.apps_entry.pack(side="left")
        ctk.CTkButton(
            f, text="💡", width=24, height=24,
            command=lambda: HelpInfoPopup(
                self, "Nombre d'applications",
                "Sur combien d'applications le travail doit-il être fait ?\n\n"
                "Exemple : Déployer un script sur VT1, VT3 et ARC = 3 apps\n\n"
                "Les Story Points de base seront multipliés\n"
                "par ce nombre (résultat plafonné à 13 max).\n\n"
                "Même tâche × 3 applications = 3x le travail."),
            fg_color="#5b8af5", hover_color="#3a6fd4").pack(side="left", padx=(4, 0))

        self.calc_btn = ctk.CTkButton(
            self, text="Calculer les Story Points",
            command=self._calculate, fg_color="#8b5cf6", hover_color="#7c3aed")
        self.calc_btn.grid(row=5, column=0, columnspan=2, padx=20, pady=15)

        self.result_var = ctk.StringVar()
        self.result_lbl = ctk.CTkLabel(
            self, textvariable=self.result_var, font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#8b5cf6")
        self.result_lbl.grid(row=6, column=0, columnspan=2, pady=10)

        self.detail_lbl = ctk.CTkLabel(self, text="", text_color="gray", wraplength=400)
        self.detail_lbl.grid(row=7, column=0, columnspan=2, padx=20, pady=5)

        self.validate_btn = ctk.CTkButton(
            self, text="Appliquer", state="disabled",
            command=self._apply)
        self.validate_btn.grid(row=8, column=0, columnspan=2, padx=20, pady=10)

    def _calculate(self):
        time_map = {
            "< 2h": 1, "< 3h30": 2, "< 14h (2j)": 3,
            "< 28h (4j)": 4, "≤ 35h (5j)": 5, "> 35h": 6
        }
        know_map = {
            "Tout": 0, "Presque tout": 1, "Quelque chose": 2,
            "Presque rien": 3, "Rien / inconnue": 4
        }
        dep_map = {
            "Aucune": 0, "Presque aucune": 1, "Quelques (≥ 3)": 2,
            "Peu (≥ 4)": 3, "Plus que peu (≥ 5)": 4, "Inconnue (?)": 5
        }

        try:
            nb_apps = max(1, int(self.apps_var.get()))
        except ValueError:
            nb_apps = 1

        t = time_map.get(self.time_var.get(), 3)
        k = know_map.get(self.know_var.get(), 2)
        d = dep_map.get(self.dep_var.get(), 2)
        total = t + k + d

        if total <= 1:
            sp_base = 1
        elif total <= 4:
            sp_base = 2
        elif total <= 7:
            sp_base = 3
        elif total <= 10:
            sp_base = 5
        elif total <= 13:
            sp_base = 8
        else:
            sp_base = 13

        sp_total = sp_base * nb_apps
        if sp_total > 13:
            sp_total = 13

        self.result_var.set(f"📊 {sp_total} Story Points")
        detail = f"SP base: {sp_base} (score: {total}) × {nb_apps} app(s)"
        if sp_base * nb_apps > 13:
            detail += f" → plafonné à 13"
        self.detail_lbl.configure(text=detail)
        self.calculated_sp = sp_total
        self.validate_btn.configure(state="normal")

    def _apply(self):
        if hasattr(self, "calculated_sp") and self.on_result:
            self.on_result(str(self.calculated_sp))
        self.destroy()


class JiraCreateUSFrame(ctk.CTkFrame):
    def __init__(self, master, config):
        super().__init__(master)
        self.config = config
        self.jira = None
        self.all_projects = {}
        self.all_epics = {}
        self.all_task_ops = [
            "ACCU - S'intégrer aux cérémonies",
            "AUTO - Agir sur les pipelines de déploiement",
            "AUTO - Interagir sur un pipeline de déploiement",
            "DATA - Anonymisation des données",
            "DATA - Anonymiser les données copiées sur un environnement autre que la production",
            "DIAG - Agir sur TEX2",
            "DIAG - Base de connaissance exploitation",
            "DIAG - Interagir sur le Tex2i",
            "DIAG - Mettre à disposition le savoir pour consolider l'exploitation industrielle (N1, N2)",
            "FLUI - Labélisation Exploitation",
            "FLUI - Respecter les processus I-TEAM",
            "FLUX - Demander, tester les ouvertures de flux",
            "FLUX - Interagir sur les certificats applicatifs",
            "FLUX - Interagir sur les VIP (URL, répartition de charge, ...)",
            "FLUX - Vérifier, remonter les blocages du WAF à la MoE",
            "HABI - Habilitation aux outils projets et techniques",
            "HARD - Vérifier les environnements livrés",
            "INFRA - Configuration des services managés",
            "INFRA - Configuration des SMAG",
            "INFRA - Gestion des ressources",
            "INFRA - Recetter les environnements",
            "INTG - S'assurer de ses accès aux outils projets et techniques",
            "INTG - S'intégrer au projet en participant aux cérémonies et en utilisant les outils projet",
            "LOGI - Maintenir à jour les OS et socles techniques",
            "LOGI - Maintenir à jour les progiciels applicatifs",
            "MNTR - Interagir sur les tableaux de bord de puits de métrique et puits de logs",
            "MNTR - Vérifier et adapter le format de log pour le puits",
            "OBSR - Agir sur la configuration des logs",
            "OBSR - Agir sur les dashboards puits de métriques et puits de log",
            "OBSR - Agir sur les notifications",
            "OBSR - Machine Learning",
            "ORDO - Agir sur les orchestrateurs métiers",
            "ORDO - Agir sur les orchestrateurs technique",
            "PLAN - Interagir sur les notifications (alerting grafana/kibana)",
            "PLAN - Interagir sur les orchestrations techniques",
            "PROC - Intégrer le respect des processus CSM SI",
            "RESI - Agir sur la configuration des conteneurs",
            "RESI - Agir sur la réplication",
            "RESI - Agir sur les groupes placement",
            "RESO - Agir sur le WAF",
            "RESO - Agir sur les certificats",
            "RESO - Agir sur les flux",
            "RESO - Agir sur les VIP",
            "SAUV - Agir sur les sauvegardes d'infrastructure et de configuration",
            "SAUV - Agir sur les sauvegardes de données méti",
            "SAUV - Interagir sur les orchestrations métier",
            "SAUV - Interagir sur une/des sauvegarde de données métier",
            "SAUV - Interagir sur une/des sauvegardes d'infrastructure ou de sa configuration",
            "SOFT - Interagir sur un job de correctifs logiciels (patch management)",
            "SURV - Agir sur les surveillances de disponibilité scénarisée",
            "SURV - Agir sur les surveillances métier",
            "SURV - Agir sur les surveillances techniqu",
            "SURV - Interagir sur une/des surveillance de disponibilité scénarisée",
            "SURV - Interagir sur une/des surveillance métier",
            "SURV - Interagir sur une/des surveillance technique",
        ]
        self.all_ticket_types = [
            "User Story Technique", "User Story", "Feature", "Anomalie (AGILE)",
            "Risque", "Demande de support", "Test", "Test Set",
            "Test Execution", "Pre-Condition", "Test Plan", "Incident"
        ]
        self.all_ust_types = [
            "User Story Technique", "UST Ops", "UST Sécurité"
        ]
        self.all_story_points = [
            "1", "2", "3", "5", "8", "13"
        ]
        self.all_priorities = [
            "Bloquant", "Majeur", "Mineure"
        ]
        self.all_components = {}
        self.active_sprint = None
        self._task_ops_after = None
        self._ticket_type_after = None
        self._ust_type_after = None
        self._story_points_after = None
        self._priority_after = None
        self._proj_search_after = None
        self._epic_search_after = None
        self._epic_search_thread = None
        self._build()
        self.after(10, self._connect)

    def _connect(self):
        url = self.config.get("jira_url")
        token = self.config.get("jira_token")
        verify = self.config.get("verify_ssl", True)
        if url and token:
            self.jira = JiraAPI(url, token, verify)
            threading.Thread(target=self._do_connect, daemon=True).start()
        else:
            self.after(0, self._render_proj_favs)
            self.after(0, self._render_epic_favs)

    def _do_connect(self):
        ok, user, _ = self.jira.test_connection()
        if ok:
            self.after(0, lambda: self._show_status(f"Connecté en tant que {user}", "green"))
            self.after(0, self._load_all_projects)
            self.after(0, self._load_template)
        else:
            self.after(0, lambda: self._show_status("Erreur de connexion — vérifiez la configuration", "red"))
        self.after(0, self._render_proj_favs)
        self.after(0, self._render_epic_favs)

    def _show_status(self, text, color):
        for w in self.result_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.result_frame, text=text, text_color=color).pack()

    def _build(self):
        self.scrollable = ctk.CTkScrollableFrame(self)
        self.scrollable.pack(fill="both", expand=True)
        self.scrollable.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.scrollable, text="Créer une User Story",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=20, pady=20, sticky="w")

        # --- Row 1 : Projet ---
        ctk.CTkLabel(self.scrollable, text="Projet:").grid(
            row=1, column=0, padx=20, pady=8, sticky="w")
        self.proj_var = ctk.StringVar()
        self.proj_entry = ctk.CTkEntry(
            self.scrollable, width=300, textvariable=self.proj_var,
            placeholder_text="Tapez pour chercher un projet...")
        self.proj_entry.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        self.proj_entry.bind("<KeyRelease>", self._filter_projects)
        self.proj_entry.bind("<FocusOut>",
                             lambda e: self.after(200, self._hide_proj_dd))
        self.proj_refresh_btn = ctk.CTkButton(
            self.scrollable, text="↻", width=30, command=self._load_all_projects)
        self.proj_refresh_btn.grid(row=1, column=2, padx=5, sticky="w")

        # Dropdown projet
        self.proj_dropdown = ctk.CTkScrollableFrame(
            self, height=150, width=300)
        self.proj_dropdown.place_forget()

        # --- Row 2 : Favoris projets ---
        self.proj_fav_frame = ctk.CTkFrame(self.scrollable, height=26, width=500)
        self.proj_fav_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=0,
                                 sticky="we")
        self.proj_fav_frame.grid_propagate(False)

        # --- Row 3 : Epic Link ---
        ctk.CTkLabel(self.scrollable, text="Epic Link:").grid(
            row=3, column=0, padx=20, pady=8, sticky="w")
        self.epic_var = ctk.StringVar()
        self.epic_entry = ctk.CTkEntry(
            self.scrollable, width=400, textvariable=self.epic_var,
            placeholder_text="Sélectionnez d'abord un projet",
            state="disabled")
        self.epic_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=8,
                             sticky="we")
        self.epic_entry.bind("<KeyRelease>", self._filter_epics)
        self.epic_entry.bind("<FocusOut>",
                             lambda e: self.after(200, self._hide_epic_dd))

        # Dropdown epic
        self.epic_dropdown = ctk.CTkScrollableFrame(
            self, height=150, width=400)
        self.epic_dropdown.place_forget()

        # --- Row 4 : Favoris epics ---
        self.epic_fav_frame = ctk.CTkFrame(self.scrollable, height=26, width=500)
        self.epic_fav_frame.grid(row=4, column=1, columnspan=2, padx=10, pady=0,
                                 sticky="we")
        self.epic_fav_frame.grid_propagate(False)

        # --- Row 5 : Titre ---
        ctk.CTkLabel(self.scrollable, text="Titre:").grid(
            row=5, column=0, padx=20, pady=8, sticky="w")
        self.title_entry = ctk.CTkEntry(self.scrollable, width=500,
            placeholder_text="[RESSOURCE][ELEMENT (facultatif)][DC][ENVIRONNEMENT] Résumé des actions")
        self.title_entry.grid(row=5, column=1, columnspan=2, padx=10, pady=8,
                              sticky="we")

        # --- Row 6 : Description ---
        ctk.CTkLabel(self.scrollable, text="Description:").grid(
            row=6, column=0, padx=20, pady=8, sticky="nw")
        self.desc_text = ctk.CTkTextbox(self.scrollable, height=160, width=500)
        self.desc_text.insert(
            "1.0", "En tant que DevOps, je veux \"OBJECTIF\" afin de \"BENEFICE ATTENDU\".\n\n"
                    "Contraintes techniques : \"OUTIL OU TECHNOLOGIE\"\n"
                    "Contraintes fonctionnelles :\n"
                    "Critères d'acceptations : ")
        self.desc_text.see("1.0")
        self.desc_text.grid(row=6, column=1, columnspan=2, padx=10, pady=8,
                            sticky="we")

        # --- Row 7 : Type de ticket ---
        ctk.CTkLabel(self.scrollable, text="Type de ticket:").grid(
            row=7, column=0, padx=20, pady=8, sticky="w")
        self.ticket_type_var = ctk.StringVar(value="User Story Technique")
        self.ticket_type_entry = ctk.CTkEntry(
            self.scrollable, width=200, textvariable=self.ticket_type_var,
            placeholder_text="Tapez pour chercher...")
        self.ticket_type_entry.grid(row=7, column=1, padx=10, pady=8, sticky="w")
        self.ticket_type_entry.bind("<KeyRelease>", self._filter_ticket_type)
        self.ticket_type_entry.bind("<FocusIn>",
                                    lambda e: self.after(100, self._show_ticket_type_dd, self.all_ticket_types))
        self.ticket_type_entry.bind("<FocusOut>",
                                    lambda e: self.after(200, self._hide_ticket_type_dd))
        self.ticket_type_dropdown = ctk.CTkFrame(
            self, height=120, width=200, corner_radius=6)
        self.ticket_type_dropdown.place_forget()

        # --- Row 8 : Type UST ---
        ctk.CTkLabel(self.scrollable, text="Type UST:").grid(
            row=8, column=0, padx=20, pady=8, sticky="w")
        self.ust_type_var = ctk.StringVar(value="UST Ops")
        self.ust_type_entry = ctk.CTkEntry(
            self.scrollable, width=200, textvariable=self.ust_type_var,
            placeholder_text="Tapez pour chercher...")
        self.ust_type_entry.grid(row=8, column=1, padx=10, pady=8, sticky="w")
        self.ust_type_entry.bind("<KeyRelease>", self._filter_ust_type)
        self.ust_type_entry.bind("<FocusIn>",
                                 lambda e: self.after(100, self._show_ust_type_dd, self.all_ust_types))
        self.ust_type_entry.bind("<FocusOut>",
                                 lambda e: self.after(200, self._hide_ust_type_dd))
        self.ust_type_dropdown = ctk.CTkFrame(
            self, height=120, width=200, corner_radius=6)
        self.ust_type_dropdown.place_forget()

        # --- Row 9 : Tâche OPS ---
        ctk.CTkLabel(self.scrollable, text="Tâche OPS:").grid(
            row=9, column=0, padx=20, pady=8, sticky="w")
        self.task_ops_var = ctk.StringVar(value="AUTO - Agir sur les pipelines de déploiement")
        self.task_ops_entry = ctk.CTkEntry(
            self.scrollable, width=400, textvariable=self.task_ops_var,
            placeholder_text="Tapez pour chercher une tâche OPS...")
        self.task_ops_entry.grid(row=9, column=1, columnspan=2, padx=10, pady=8,
                                 sticky="we")
        self.task_ops_entry.bind("<KeyRelease>", self._filter_task_ops)
        self.task_ops_entry.bind("<FocusIn>",
                                 lambda e: self.after(100, self._show_task_ops_dd, sorted(self.all_task_ops)))
        self.task_ops_entry.bind("<FocusOut>",
                                 lambda e: self.after(200, self._hide_task_ops_dd))

        self.task_ops_dropdown = ctk.CTkScrollableFrame(
            self, height=150, width=400)
        self.task_ops_dropdown.place_forget()

        # --- Row 10 : Story Points ---
        ctk.CTkLabel(self.scrollable, text="Story Points:").grid(
            row=10, column=0, padx=20, pady=8, sticky="w")
        self.story_points_var = ctk.StringVar()
        self.story_points_entry = ctk.CTkEntry(
            self.scrollable, width=80, textvariable=self.story_points_var,
            placeholder_text="SP")
        self.story_points_entry.grid(row=10, column=1, padx=10, pady=8, sticky="w")
        self.story_points_entry.bind("<KeyRelease>", self._filter_story_points)
        self.story_points_entry.bind("<FocusIn>",
                                     lambda e: self.after(100, self._show_story_points_dd, self.all_story_points))
        self.story_points_entry.bind("<FocusOut>",
                                     lambda e: self.after(200, self._hide_story_points_dd))
        self.story_points_dropdown = ctk.CTkFrame(
            self, height=167, width=80, corner_radius=6)
        self.story_points_dropdown.place_forget()

        self.auto_sp_btn = ctk.CTkButton(
            self.scrollable, text="Auto", width=50,
            command=self._show_sp_estimator,
            fg_color="#8b5cf6", hover_color="#7c3aed")
        self.auto_sp_btn.grid(row=10, column=2, padx=(0, 10), sticky="w")

        # --- Row 11 : Priorité ---
        ctk.CTkLabel(self.scrollable, text="Priorité:").grid(
            row=11, column=0, padx=20, pady=8, sticky="w")
        self.priority_var = ctk.StringVar()
        self.priority_entry = ctk.CTkEntry(
            self.scrollable, width=150, textvariable=self.priority_var,
            placeholder_text="Tapez pour chercher...")
        self.priority_entry.grid(row=11, column=1, padx=10, pady=8, sticky="w")
        self.priority_entry.bind("<KeyRelease>", self._filter_priority)
        self.priority_entry.bind("<FocusIn>",
                                 lambda e: self.after(100, self._show_priority_dd, self.all_priorities))
        self.priority_entry.bind("<FocusOut>",
                                 lambda e: self.after(200, self._hide_priority_dd))
        self.priority_dropdown = ctk.CTkFrame(
            self, height=100, width=150, corner_radius=6)
        self.priority_dropdown.place_forget()

        # --- Row 12 : Composants ---
        ctk.CTkLabel(self.scrollable, text="Composant:").grid(
            row=12, column=0, padx=20, pady=8, sticky="w")
        self.component_var = ctk.StringVar()
        self.component_entry = ctk.CTkEntry(
            self.scrollable, width=200, textvariable=self.component_var,
            placeholder_text="Sélectionnez d'abord un projet...")
        self.component_entry.grid(row=12, column=1, padx=10, pady=8, sticky="w")
        self.component_entry.bind("<KeyRelease>", self._filter_components)
        self.component_entry.bind("<FocusIn>",
                                  lambda e: self.after(100, self._show_component_dd, sorted(self.all_components.keys()) if self.all_components else []))
        self.component_entry.bind("<FocusOut>",
                                  lambda e: self.after(200, self._hide_component_dd))
        self.component_dropdown = ctk.CTkScrollableFrame(
            self, height=120, width=200)
        self.component_dropdown.place_forget()

        # --- Row 13 : Sprint actif ---
        self.sprint_var = ctk.BooleanVar(value=False)
        self.sprint_cb = ctk.CTkCheckBox(
            self.scrollable, text="Ajouter au sprint actif",
            variable=self.sprint_var)
        self.sprint_cb.grid(row=13, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        self.sprint_lbl = ctk.CTkLabel(self.scrollable, text="", text_color="gray", font=ctk.CTkFont(size=10))
        self.sprint_lbl.grid(row=13, column=2, padx=10, pady=5, sticky="w")

        # --- Row 14 : Bouton ---
        self.create_btn = ctk.CTkButton(
            self.scrollable, text="Créer la User Story",
            command=self._create_us, fg_color="#2b6cb0", hover_color="#2c5282")
        self.create_btn.grid(row=14, column=0, columnspan=3, padx=20, pady=15)

        # --- Row 15 : Résultat ---
        self.result_frame = ctk.CTkFrame(self.scrollable)
        self.result_frame.grid(row=15, column=0, columnspan=3, padx=20, pady=5,
                               sticky="we")

    # ============================================================
    # PROJETS
    # ============================================================

    def _load_all_projects(self):
        if self.jira:
            threading.Thread(target=self._do_load_projects, daemon=True).start()

    def _do_load_projects(self):
        try:
            projects = self.jira.get_projects()
            if not projects:
                self.after(0, self._projects_error, "Aucun projet retourné")
                return
            ap = [(p.get("key", ""), p.get("name", "")) for p in projects]
            self.after(0, self._projects_loaded, ap)
        except Exception as e:
            self.after(0, lambda m=str(e): self._projects_error(m))

    def _projects_loaded(self, projects_list):
        self.all_projects = {f"{key} - {name}": key for key, name in projects_list}
        self._all_proj_keys = projects_list
        n = len(self.all_projects)
        self.proj_entry.configure(
            placeholder_text=f"{n} projet(s) chargé(s). Tapez pour filtrer...")
        self._render_proj_favs()

    def _projects_error(self, msg):
        self.proj_entry.configure(placeholder_text=f"Erreur: {msg}")

    def _filter_projects(self, event=None):
        if event and event.keysym in ("Up", "Down", "Return", "Escape"):
            return
        if self._proj_search_after:
            self.after_cancel(self._proj_search_after)
        self._proj_search_after = self.after(150, self._do_filter_projects)

    def _do_filter_projects(self):
        self._proj_search_after = None
        if not self.all_projects:
            self._hide_proj_dd()
            return
        search = self.proj_var.get().lower().strip()
        if not search:
            favs = set(self.config.get("favorite_projects", []))
            fav_list = sorted(f"{k} - {n}" for k, n in self._all_proj_keys if k in favs)
            other = sorted(f"{k} - {n}" for k, n in self._all_proj_keys if k not in favs)
            ordered = fav_list + other
            self._show_proj_dd(ordered[:50])
            return
        threading.Thread(target=self._do_search_projects, args=(search,), daemon=True).start()

    def _do_search_projects(self, search):
        favs = set(self.config.get("favorite_projects", []))
        fav_list = [f"{k} - {n}" for k, n in self._all_proj_keys if k in favs and search in f"{k} {n}".lower()]
        other = [f"{k} - {n}" for k, n in self._all_proj_keys if k not in favs and search in f"{k} {n}".lower()]
        ordered = sorted(fav_list) + sorted(other)
        self.after(0, lambda o=ordered: self._show_proj_dd(o[:50]))

    def _hide_proj_dd(self):
        self.proj_dropdown.place_forget()

    def _show_proj_dd(self, items):
        for w in self.proj_dropdown.winfo_children():
            w.destroy()
        favs = set(self.config.get("favorite_projects", []))
        row = 0
        for item in items:
            key = self.all_projects.get(item, "")
            is_fav = key in favs

            def _make_toggle_btn(k):
                def _toggle():
                    self._toggle_proj_fav(k)
                return _toggle

            star_btn = ctk.CTkButton(
                self.proj_dropdown, text="★" if is_fav else "☆", width=25,
                command=_make_toggle_btn(key),
                fg_color="transparent", text_color="#f0b429", hover_color="#e09400")
            star_btn.grid(row=row, column=0, padx=0, pady=1, sticky="e")
            btn = ctk.CTkButton(
                self.proj_dropdown, text=item, anchor="w",
                command=lambda t=item: self._select_project(t),
                fg_color="transparent", text_color=("black", "white"),
                hover_color="#3a7bc8", height=25)
            btn.grid(row=row, column=0, padx=(0, 30), pady=1, sticky="we")
            row += 1
        self.proj_dropdown.place(in_=self.proj_entry, x=0, rely=1, relx=0,
                                 y=3, anchor="nw")
        self.proj_dropdown.lift()

    def _select_project(self, label):
        self.proj_var.set(label)
        self._hide_proj_dd()
        self._on_project_change(label)

    def _toggle_proj_fav(self, key):
        favs = set(self.config.get("favorite_projects", []))
        if key in favs:
            favs.discard(key)
        else:
            favs.add(key)
        self.config["favorite_projects"] = list(favs)
        save_config(self.config)
        self._render_proj_favs()
        search = self.proj_var.get().lower().strip()
        if search:
            threading.Thread(target=self._do_search_projects, args=(search,), daemon=True).start()

    def _render_proj_favs(self):
        for w in self.proj_fav_frame.winfo_children():
            w.destroy()
        favs = self.config.get("favorite_projects", [])
        if not favs:
            ctk.CTkLabel(self.proj_fav_frame, text="Aucun favori (★ depuis la liste)",
                         text_color="gray", font=ctk.CTkFont(size=9)).pack(
                side="left", padx=5)
            return
        for key in favs:
            btn = ctk.CTkButton(
                self.proj_fav_frame, text=f"★ {key}", width=70, height=20,
                font=ctk.CTkFont(size=9),
                command=lambda k=key: self._select_fav_project(k),
                fg_color="#f0b429", text_color="black", hover_color="#e09400")
            btn.pack(side="left", padx=2, pady=2)

    def _select_fav_project(self, key):
        label = f"{key} - {key}"
        for lbl, k in self.all_projects.items():
            if k == key:
                label = lbl
                break
        self.proj_var.set(label)
        self._hide_proj_dd()
        self._on_project_change(label)

    def _show_sp_estimator(self):
        SPEstimatorPopup(
            self,
            on_result=lambda sp: self.story_points_var.set(sp)
        )

    # ============================================================
    # TEMPLATE
    # ============================================================

    def _load_template(self):
        tmpl = self.config.get("template_us", {})
        if tmpl.get("description"):
            self.desc_text.delete("1.0", "end")
            self.desc_text.insert("1.0", tmpl["description"])

    # ============================================================
    # FEATURES
    # ============================================================

    def _on_project_change(self, value=None):
        if not self.jira:
            return
        self.epic_var.set("")
        self.all_epics = {}
        self.epic_entry.configure(state="normal",
                                  placeholder_text="Tapez pour chercher une Feature...")
        self._hide_epic_dd()
        self._render_epic_favs()
        self.component_var.set("")
        self.all_components = {}
        self.component_entry.configure(placeholder_text="Chargement...")
        self.sprint_var.set(False)
        self.active_sprint = None
        self.sprint_lbl.configure(text="")
        proj_key = self.all_projects.get(value, "")
        if proj_key:
            self.task_ops_entry.configure(placeholder_text="Chargement...")
            threading.Thread(target=self._do_load_components_and_sprint,
                             args=(proj_key,), daemon=True).start()
            threading.Thread(target=self._do_load_task_ops,
                             args=(proj_key,), daemon=True).start()
            threading.Thread(target=self._do_load_issue_types,
                             args=(proj_key,), daemon=True).start()

    def _do_load_components_and_sprint(self, proj_key):
        try:
            comps = self.jira.get_components(proj_key)
            comp_dict = {}
            comp_names = []
            for c in comps:
                name = c.get("name", "")
                comp_dict[name] = c.get("id")
                comp_names.append(name)
            sprint = self.jira.get_active_sprint(proj_key)
            self.after(0, self._components_and_sprint_loaded, comp_names, comp_dict, sprint)
        except Exception as e:
            self.after(0, self._components_error, str(e))

    def _components_and_sprint_loaded(self, comp_names, comp_dict, sprint):
        self.all_components = comp_dict
        self.component_entry.configure(placeholder_text="Tapez pour chercher...")
        if sprint:
            self.active_sprint = sprint
            self.sprint_lbl.configure(text=sprint.get("name", ""))
            self.sprint_var.set(True)

    def _components_error(self, err):
        self.component_entry.configure(placeholder_text="Erreur chargement")

    def _do_load_task_ops(self, proj_key):
        try:
            ops = self.jira.get_task_ops(proj_key)
            if ops:
                self.after(0, self._task_ops_loaded, ops)
        except Exception:
            pass

    def _task_ops_loaded(self, ops):
        self.all_task_ops = ops
        self.task_ops_entry.configure(placeholder_text="Tapez pour chercher une tâche OPS...")

    def _do_load_issue_types(self, proj_key):
        try:
            types = self.jira.get_issue_types(proj_key)
            if types:
                self.after(0, self._issue_types_loaded, types)
        except Exception:
            pass

    def _issue_types_loaded(self, types):
        self.all_ticket_types = types
        if self.ticket_type_var.get() not in types:
            self.ticket_type_var.set("")

    def _search_epics(self, search_text=""):
        self._epic_search_thread = None
        try:
            epics = self.jira.search_epics(search_text)
            ae = {}
            for e in epics:
                key = e.get("key", "")
                summary = e.get("fields", {}).get("summary", "")
                ae[summary] = key
            items = sorted(ae.keys())
            fav_epics = self.config.get("favorite_epics", {})
            if isinstance(fav_epics, list):
                fav_keys = set(fav_epics)
            else:
                fav_keys = set(fav_epics.keys())
            fav_items = [i for i in items if ae.get(i) in fav_keys]
            other_items = [i for i in items if ae.get(i) not in fav_keys]
            ordered = fav_items[:50] + other_items[:50]
            self.after(0, lambda a=ae, i=ordered: self._epics_search_done(a, i))
        except Exception as err:
            msg = str(err)
            self.after(0, lambda m=msg: self._epics_error(m))

    def _epics_search_done(self, ae, items):
        self.all_epics = ae
        self._render_epic_favs()
        current = self.epic_var.get().strip()
        if current and len(current) >= 2 and items:
            self.epic_entry.configure(
                state="normal",
                placeholder_text=f"{len(items)} résultat(s). Tapez pour affiner...")
            self._show_epic_dd(items)
        elif not items:
            self.epic_entry.configure(
                state="normal",
                placeholder_text="Aucun résultat")

    def _epics_error(self, msg):
        self.all_epics = {}
        self.epic_entry.configure(
            state="normal",
            placeholder_text=f"Erreur: {msg}")

    def _filter_epics(self, event=None):
        if event and event.keysym in ("Up", "Down", "Return", "Escape"):
            return
        if self._epic_search_after:
            self.after_cancel(self._epic_search_after)
        self._epic_search_after = self.after(300, self._do_filter_epics)

    def _do_filter_epics(self):
        self._epic_search_after = None
        search = self.epic_var.get().strip()
        if not search or len(search) < 2:
            self._hide_epic_dd()
            return
        if self.all_epics:
            filtered = sorted(k for k in self.all_epics
                              if search.lower() in k.lower())
            if filtered:
                fav_epics = self.config.get("favorite_epics", {})
                if isinstance(fav_epics, list):
                    fav_keys = set(fav_epics)
                else:
                    fav_keys = set(fav_epics.keys())
                fav_items = [k for k in filtered if self.all_epics.get(k) in fav_keys]
                other_items = [k for k in filtered if self.all_epics.get(k) not in fav_keys]
                self._show_epic_dd((fav_items + other_items)[:50])
                return
        if self._epic_search_thread and self._epic_search_thread.is_alive():
            return
        self.epic_entry.configure(state="normal",
                                  placeholder_text="Recherche en cours...")
        self._epic_search_thread = threading.Thread(target=self._search_epics, args=(search,),
                         daemon=True)
        self._epic_search_thread.start()

    def _hide_epic_dd(self):
        self.epic_dropdown.place_forget()

    def _show_epic_dd(self, items):
        for w in self.epic_dropdown.winfo_children():
            w.destroy()
        row = 0
        for item in items:
            key = self.all_epics.get(item, "")
            fav_epics = self.config.get("favorite_epics", {})
            if isinstance(fav_epics, list):
                fav_epics = {k: k for k in fav_epics}
            is_fav = key in fav_epics

            def _make_toggle_btn(k, summary):
                def _toggle():
                    self._toggle_epic_fav(k, summary)
                return _toggle

            star_btn = ctk.CTkButton(
                self.epic_dropdown, text="★" if is_fav else "☆", width=25,
                command=_make_toggle_btn(key, item),
                fg_color="transparent", text_color="#f0b429", hover_color="#e09400")
            star_btn.grid(row=row, column=0, padx=0, pady=1, sticky="e")
            btn = ctk.CTkButton(
                self.epic_dropdown, text=item, anchor="w",
                command=lambda t=item: self._select_epic(t),
                fg_color="transparent", text_color=("black", "white"),
                hover_color="#3a7bc8", height=25)
            btn.grid(row=row, column=0, padx=(0, 30), pady=1, sticky="we")
            row += 1
        self.epic_dropdown.place(in_=self.epic_entry, x=0, rely=1, relx=0,
                                 y=3, anchor="nw")
        self.epic_dropdown.lift()

    def _select_epic(self, label):
        self.epic_var.set(label)
        self._hide_epic_dd()

    def _toggle_epic_fav(self, key, summary):
        fav_epics = self.config.get("favorite_epics", {})
        if isinstance(fav_epics, list):
            fav_epics = {k: k for k in fav_epics}
        if key in fav_epics:
            del fav_epics[key]
        else:
            fav_epics[key] = summary
        self.config["favorite_epics"] = fav_epics
        save_config(self.config)
        self._render_epic_favs()
        search = self.epic_var.get().strip()
        if search and len(search) >= 2:
            filtered = sorted(k for k in self.all_epics
                              if search.lower() in k.lower())
            if filtered:
                fav_items = [k for k in filtered if self.all_epics.get(k) in fav_epics]
                other_items = [k for k in filtered if self.all_epics.get(k) not in fav_epics]
                self._show_epic_dd(fav_items + other_items)

    def _render_epic_favs(self):
        for w in self.epic_fav_frame.winfo_children():
            w.destroy()
        fav_epics = self.config.get("favorite_epics", {})
        if isinstance(fav_epics, list):
            fav_epics = {k: k for k in fav_epics}
            self.config["favorite_epics"] = fav_epics
            save_config(self.config)
        if not fav_epics:
            ctk.CTkLabel(self.epic_fav_frame, text="Aucun favori (★ depuis la liste)",
                         text_color="gray", font=ctk.CTkFont(size=9)).pack(
                side="left", padx=5)
            return
        for key, summary in fav_epics.items():
            btn = ctk.CTkButton(
                self.epic_fav_frame, text=f"★ {summary}", width=100, height=20,
                font=ctk.CTkFont(size=9),
                command=lambda k=key: self._select_fav_epic(k),
                fg_color="#f0b429", text_color="black", hover_color="#e09400")
            btn.pack(side="left", padx=2, pady=2)

    def _select_fav_epic(self, key):
        for lbl, k in self.all_epics.items():
            if k == key:
                self.epic_var.set(lbl)
                self._hide_epic_dd()
                return
        fav_epics = self.config.get("favorite_epics", {})
        if isinstance(fav_epics, dict) and key in fav_epics:
            summary = fav_epics[key]
            self.epic_var.set(summary)
            self.all_epics[summary] = key
            self._hide_epic_dd()

    # ============================================================
    # TYPE DE TICKET
    # ============================================================

    def _filter_ticket_type(self, event=None):
        if event and event.keysym == "Escape":
            self._hide_ticket_type_dd()
            return
        if event and event.keysym == "Return":
            items = [w.cget("text") for w in self.ticket_type_dropdown.winfo_children() if w.cget("text")]
            if items:
                self._select_ticket_type(items[0])
            return
        if event and event.keysym in ("Up", "Down"):
            return
        if self._ticket_type_after:
            self.after_cancel(self._ticket_type_after)
        self._ticket_type_after = self.after(150, self._do_filter_ticket_type)

    def _do_filter_ticket_type(self):
        self._ticket_type_after = None
        search = self.ticket_type_var.get().lower().strip()
        filtered = sorted(t for t in self.all_ticket_types if search in t.lower()) if search else self.all_ticket_types
        if filtered:
            self._show_ticket_type_dd(filtered)
        else:
            self._hide_ticket_type_dd()

    def _show_ticket_type_dd(self, items):
        for w in self.ticket_type_dropdown.winfo_children():
            w.destroy()
        for item in items:
            btn = ctk.CTkButton(
                self.ticket_type_dropdown, text=item, anchor="w",
                command=lambda t=item: self._select_ticket_type(t),
                fg_color="transparent", text_color=("black", "white"),
                hover_color="#3a7bc8", height=25)
            btn.pack(fill="x", pady=1, padx=2)
        h = len(items) * 27 + 5
        self.ticket_type_dropdown.configure(height=min(h, 200))
        self.ticket_type_dropdown.place(in_=self.ticket_type_entry, x=0, rely=1, relx=0,
                                        y=3, anchor="nw")
        self.ticket_type_dropdown.lift()

    def _hide_ticket_type_dd(self):
        self.ticket_type_dropdown.place_forget()

    def _select_ticket_type(self, label):
        self.ticket_type_var.set(label)
        self._hide_ticket_type_dd()

    # ============================================================
    # TYPE UST
    # ============================================================

    def _filter_ust_type(self, event=None):
        if event and event.keysym == "Escape":
            self._hide_ust_type_dd()
            return
        if event and event.keysym == "Return":
            items = [w.cget("text") for w in self.ust_type_dropdown.winfo_children() if w.cget("text")]
            if items:
                self._select_ust_type(items[0])
            return
        if event and event.keysym in ("Up", "Down"):
            return
        if self._ust_type_after:
            self.after_cancel(self._ust_type_after)
        self._ust_type_after = self.after(150, self._do_filter_ust_type)

    def _do_filter_ust_type(self):
        self._ust_type_after = None
        search = self.ust_type_var.get().lower().strip()
        filtered = sorted(t for t in self.all_ust_types if search in t.lower()) if search else self.all_ust_types
        if filtered:
            self._show_ust_type_dd(filtered)
        else:
            self._hide_ust_type_dd()

    def _show_ust_type_dd(self, items):
        for w in self.ust_type_dropdown.winfo_children():
            w.destroy()
        for item in items:
            btn = ctk.CTkButton(
                self.ust_type_dropdown, text=item, anchor="w",
                command=lambda t=item: self._select_ust_type(t),
                fg_color="transparent", text_color=("black", "white"),
                hover_color="#3a7bc8", height=25)
            btn.pack(fill="x", pady=1, padx=2)
        h = len(items) * 27 + 5
        self.ust_type_dropdown.configure(height=min(h, 200))
        self.ust_type_dropdown.place(in_=self.ust_type_entry, x=0, rely=1, relx=0,
                                     y=3, anchor="nw")
        self.ust_type_dropdown.lift()

    def _hide_ust_type_dd(self):
        self.ust_type_dropdown.place_forget()

    def _select_ust_type(self, label):
        self.ust_type_var.set(label)
        self._hide_ust_type_dd()

    # ============================================================
    # STORY POINTS
    # ============================================================

    def _filter_story_points(self, event=None):
        if event and event.keysym == "Escape":
            self._hide_story_points_dd()
            return
        if event and event.keysym == "Return":
            items = [w.cget("text") for w in self.story_points_dropdown.winfo_children() if w.cget("text")]
            if items:
                self._select_story_points(items[0])
            return
        if event and event.keysym in ("Up", "Down"):
            return
        if self._story_points_after:
            self.after_cancel(self._story_points_after)
        self._story_points_after = self.after(150, self._do_filter_story_points)

    def _do_filter_story_points(self):
        self._story_points_after = None
        search = self.story_points_var.get().strip()
        if not search:
            self._show_story_points_dd(self.all_story_points)
            return
        filtered = [t for t in self.all_story_points if search in t]
        if filtered:
            self._show_story_points_dd(filtered)
        else:
            self._hide_story_points_dd()

    def _show_story_points_dd(self, items):
        for w in self.story_points_dropdown.winfo_children():
            w.destroy()
        for item in items:
            btn = ctk.CTkButton(
                self.story_points_dropdown, text=item, anchor="w",
                command=lambda t=item: self._select_story_points(t),
                fg_color="transparent", text_color=("black", "white"),
                hover_color="#3a7bc8", height=25)
            btn.pack(fill="x", pady=1, padx=2)
        h = len(items) * 27 + 5
        self.story_points_dropdown.configure(height=min(h, 200))
        self.story_points_dropdown.place(in_=self.story_points_entry, x=0, rely=1, relx=0,
                                         y=3, anchor="nw")
        self.story_points_dropdown.lift()

    def _hide_story_points_dd(self):
        self.story_points_dropdown.place_forget()

    def _select_story_points(self, label):
        self.story_points_var.set(label)
        self._hide_story_points_dd()

    # ============================================================
    # PRIORITÉ
    # ============================================================

    def _filter_priority(self, event=None):
        if event and event.keysym == "Escape":
            self._hide_priority_dd()
            return
        if event and event.keysym == "Return":
            items = [w.cget("text") for w in self.priority_dropdown.winfo_children() if w.cget("text")]
            if items:
                self._select_priority(items[0])
            return
        if event and event.keysym in ("Up", "Down"):
            return
        if self._priority_after:
            self.after_cancel(self._priority_after)
        self._priority_after = self.after(150, self._do_filter_priority)

    def _do_filter_priority(self):
        self._priority_after = None
        search = self.priority_var.get().lower().strip()
        if not search:
            self._show_priority_dd(self.all_priorities)
            return
        filtered = sorted(t for t in self.all_priorities if search in t.lower())
        if filtered:
            self._show_priority_dd(filtered)
        else:
            self._hide_priority_dd()

    def _show_priority_dd(self, items):
        for w in self.priority_dropdown.winfo_children():
            w.destroy()
        for item in items:
            btn = ctk.CTkButton(
                self.priority_dropdown, text=item, anchor="w",
                command=lambda t=item: self._select_priority(t),
                fg_color="transparent", text_color=("black", "white"),
                hover_color="#3a7bc8", height=25)
            btn.pack(fill="x", pady=1, padx=2)
        h = len(items) * 27 + 5
        self.priority_dropdown.configure(height=min(h, 150))
        self.priority_dropdown.place(in_=self.priority_entry, x=0, rely=1, relx=0,
                                     y=3, anchor="nw")
        self.priority_dropdown.lift()

    def _hide_priority_dd(self):
        self.priority_dropdown.place_forget()

    def _select_priority(self, label):
        self.priority_var.set(label)
        self._hide_priority_dd()

    # ============================================================
    # COMPOSANTS
    # ============================================================

    def _filter_components(self, event=None):
        if event and event.keysym == "Escape":
            self._hide_component_dd()
            return
        if event and event.keysym == "Return":
            items = [w.cget("text") for w in self.component_dropdown.winfo_children() if w.cget("text")]
            if items:
                self._select_component(items[0])
            return
        if event and event.keysym in ("Up", "Down"):
            return
        search = self.component_var.get().lower().strip()
        if not search:
            self._show_component_dd(sorted(self.all_components.keys()))
            return
        filtered = sorted(c for c in self.all_components.keys() if search in c.lower())
        if filtered:
            self._show_component_dd(filtered)
        else:
            self._hide_component_dd()

    def _show_component_dd(self, items):
        for w in self.component_dropdown.winfo_children():
            w.destroy()
        for item in items:
            btn = ctk.CTkButton(
                self.component_dropdown, text=item, anchor="w",
                command=lambda t=item: self._select_component(t),
                fg_color="transparent", text_color=("black", "white"),
                hover_color="#3a7bc8", height=25)
            btn.pack(fill="x", pady=1)
        self.component_dropdown.place(in_=self.component_entry, x=0, rely=1, relx=0,
                                      y=3, anchor="nw")
        self.component_dropdown.lift()

    def _hide_component_dd(self):
        self.component_dropdown.place_forget()

    def _select_component(self, label):
        self.component_var.set(label)
        self._hide_component_dd()

    # ============================================================
    # TÂCHE OPS
    # ============================================================

    def _filter_task_ops(self, event=None):
        if event and event.keysym == "Escape":
            self._hide_task_ops_dd()
            return
        if event and event.keysym == "Return":
            items = [w.cget("text") for w in self.task_ops_dropdown.winfo_children() if w.cget("text")]
            if items:
                self._select_task_ops(items[0])
            return
        if event and event.keysym in ("Up", "Down"):
            return
        if self._task_ops_after:
            self.after_cancel(self._task_ops_after)
        self._task_ops_after = self.after(150, self._do_filter_task_ops)

    def _do_filter_task_ops(self):
        self._task_ops_after = None
        search = self.task_ops_var.get().lower().strip()
        if not search:
            self._show_task_ops_dd(sorted(self.all_task_ops)[:30])
            return
        filtered = sorted(t for t in self.all_task_ops if search in t.lower())
        if filtered:
            self._show_task_ops_dd(filtered[:30])
        else:
            self._hide_task_ops_dd()

    def _show_task_ops_dd(self, items):
        for w in self.task_ops_dropdown.winfo_children():
            w.destroy()
        row = 0
        for item in items:
            btn = ctk.CTkButton(
                self.task_ops_dropdown, text=item, anchor="w",
                command=lambda t=item: self._select_task_ops(t),
                fg_color="transparent", text_color=("black", "white"),
                hover_color="#3a7bc8", height=25)
            btn.grid(row=row, column=0, pady=1, sticky="we")
            row += 1
        self.task_ops_dropdown.place(in_=self.task_ops_entry, x=0, rely=1, relx=0,
                                     y=3, anchor="nw")
        self.task_ops_dropdown.lift()

    def _hide_task_ops_dd(self):
        self.task_ops_dropdown.place_forget()

    def _select_task_ops(self, label):
        self.task_ops_var.set(label)
        self._hide_task_ops_dd()

    # ============================================================
    # CRÉATION
    # ============================================================

    def _create_us(self):
        if not self.jira:
            messagebox.showerror("Erreur", "Configurez d'abord Jira")
            return
        proj_key = self.all_projects.get(self.proj_var.get(), "")
        if not proj_key:
            messagebox.showerror("Erreur", "Sélectionnez un projet valide")
            return
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Erreur", "Veuillez entrer un titre")
            return

        desc = self.desc_text.get("1.0", "end").strip()
        ticket_type = self.ticket_type_var.get()
        ust_type = self.ust_type_var.get()
        task_ops = self.task_ops_var.get()
        sp = self.story_points_var.get().strip()
        story_points = int(sp) if sp else None
        priority = self.priority_var.get() if self.priority_var.get() else None

        feature_key = None
        ev = self.epic_var.get()
        if ev:
            feature_key = self.all_epics.get(ev)

        component = self.component_var.get().strip() if self.component_var.get() else None
        sprint_id = self.active_sprint.get("id") if self.sprint_var.get() and self.active_sprint else None

        self.create_btn.configure(state="disabled", text="Création en cours...")
        self._show_status("Création en cours...", "blue")
        assignee = self.jira.user
        threading.Thread(target=self._do_create,
                         args=(proj_key, title, desc, ticket_type, ust_type, task_ops,
                               story_points, priority, feature_key, assignee, component, sprint_id),
                         daemon=True).start()

    def _do_create(self, pk, title, desc, tt, ut, to, sp, prio, fk, assignee, component, sprint_id):
        import logging
        try:
            logging.debug("Creating US: pk=%s tt=%s ut=%s to=%s sp=%s prio=%s fk=%s assignee=%s comp=%s sprint=%s",
                          pk, tt, ut, to, sp, prio, fk, assignee, component, sprint_id)
            ok, key, err = self.jira.create_user_story(
                pk, title, desc, ticket_type=tt, ust_type=ut, task_ops=to,
                story_points=sp, priority=prio, feature_key=fk, assignee=assignee,
                component=component, sprint_id=sprint_id)
            logging.debug("Create result: ok=%s key=%s", ok, key)
        except Exception as e:
            logging.exception("Create exception")
            ok, key, err = False, None, str(e)
        self.after(0, self._create_done, ok, key, err)

    def _create_done(self, ok, key, err):
        self.create_btn.configure(state="normal", text="Créer la User Story")
        for w in self.result_frame.winfo_children():
            w.destroy()
        if ok:
            lbl = ctk.CTkLabel(self.result_frame, text="Succès !", text_color="green",
                               font=ctk.CTkFont(size=14, weight="bold"))
            lbl.pack(side="left", padx=0)
            link = ctk.CTkLabel(self.result_frame, text=f"{key}",
                                text_color="#3a86c8", cursor="hand2",
                                font=ctk.CTkFont(size=14, underline=True))
            link.pack(side="left", padx=(4, 0))
            link.bind("<Button-1>",
                      lambda e: self._open_url(f"{self.jira.url}/browse/{key}"))
            self.config.setdefault("last_created", []).append(key)
            save_config(self.config)
        else:
            ctk.CTkLabel(self.result_frame, text=f"Erreur: {err}",
                         text_color="red").pack()

    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)


class JiraUSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jira User Story Creator")
        self.geometry("700x950")
        self.minsize(650, 880)
        self.config = load_config()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        self.tab_config = self.tabview.add("Configuration")
        self.tab_create = self.tabview.add("Créer User Story")

        self.config_frame = JiraConfigFrame(
            self.tab_config, self.config, on_saved=self._on_config_saved)
        self.config_frame.pack(fill="both", expand=True)

        self.create_frame = JiraCreateUSFrame(self.tab_create, self.config)
        self.create_frame.pack(fill="both", expand=True)

        # Hook tab changes (both clicks and programmatic set())
        self.tabview._command = lambda: self.after(50, self._resize_to_fit)
        original_set = self.tabview.set
        def _on_set(name):
            original_set(name)
            self.after(50, self._resize_to_fit)
        self.tabview.set = _on_set

        has_token = bool(self.config.get("jira_token", "").strip())
        if has_token:
            self.tabview.set("Créer User Story")

        self.after(100, self._resize_to_fit)
        self.after(3000, lambda: check_for_updates(self))

    def _resize_to_fit(self):
        self.update_idletasks()
        current = self.tabview.get()
        tab = self.tabview.tab(current)
        h = tab.winfo_reqheight() + 80
        h = max(500, min(h, 950))
        self.geometry(f"700x{int(h)}")

    def _on_close(self):
        url = self.config_frame.url_entry.get().strip()
        token = self.config_frame.token_entry.get().strip()
        if url and token:
            self.config["jira_url"] = url
            self.config["jira_token"] = token
            self.config["verify_ssl"] = self.config_frame.ssl_var.get()
        save_config(self.config)
        self.destroy()

    def _on_config_saved(self):
        self.config = load_config()
        self.create_frame.config = self.config
        self.create_frame._connect()
        self.create_frame._load_all_projects()


def main():
    app = JiraUSApp()
    app.mainloop()


if __name__ == "__main__":
    main()
