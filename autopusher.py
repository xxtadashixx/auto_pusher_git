import os
import subprocess
import shutil
from datetime import datetime

def run_command(command, check=True):
    """Exécute une commande shell."""
    result = subprocess.run(command, shell=True, text=True)
    if check and result.returncode != 0:
        print("❌ Une erreur est survenue.")
        exit()

def branch_exists(branch_name):
    """Vérifie si une branche locale existe."""
    result = subprocess.run(f"git branch --list {branch_name}", shell=True, text=True, capture_output=True)
    return branch_name in result.stdout

def remote_exists():
    """Vérifie si un remote 'origin' est déjà configuré."""
    result = subprocess.run("git remote", shell=True, text=True, capture_output=True)
    return 'origin' in result.stdout

def delete_branch(branch_name):
    """Supprime une branche locale."""
    run_command(f"git branch -D {branch_name}")

def backup_before_merge(repo_path):
    """Crée une sauvegarde du dossier avant un merge."""
    backup_folder = os.path.join(repo_path, f"backup_before_merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copytree(repo_path, backup_folder, ignore=shutil.ignore_patterns(".git", "backup*"))
    print(f"🗃️ Dossier sauvegardé dans : {backup_folder}")

def team_menu(repo_path):
    """Menu pour travailler en équipe."""
    while True:
        print("\n👥 Menu travail en équipe :")
        print("1) `git pull`")
        print("2) `git merge` une branche")
        print("3) Voir `git status`")
        print("4) Voir `git log --oneline`")
        print("5) Voir `git diff`")
        print("6) Revenir au menu principal")

        choice = input("Votre choix (1-6) : ").strip()

        if choice == '1':
            run_command("git pull")
        elif choice == '2':
            other_branch = input("🔀 Nom de la branche à merger dans la tienne : ").strip()
            backup_before_merge(repo_path)
            run_command(f"git merge {other_branch}")
        elif choice == '3':
            run_command("git status", check=False)
        elif choice == '4':
            run_command("git log --oneline", check=False)
        elif choice == '5':
            run_command("git diff", check=False)
        elif choice == '6':
            break
        else:
            print("❌ Choix invalide.")

def main():
    print("🎉 Bienvenue dans AutoPusher v2.0 🚀")

    # 1. Choisir le dossier
    repo_path = input("📁 Coller le chemin du dossier à pusher : ").strip()
    os.chdir(repo_path)
    print(f"📂 Répertoire actuel : {os.getcwd()}")

    # 2. Initialiser si besoin
    if not os.path.exists(".git"):
        init = input("🔧 Initialiser un dépôt Git ici ? (y/n) : ").lower()
        if init == 'y':
            run_command("git init")

    # 3. Ajouter fichiers
    specific_path = input("➕ Ajouter un fichier/dossier spécifique ? Sinon Entrée pour tout ajouter : ").strip()
    if specific_path:
        run_command(f"git add {specific_path}")
    else:
        run_command("git add .")

    # 4. Commit
    commit_msg = input("📝 Message de commit : ").strip()
    run_command(f'git commit -m "{commit_msg}"')

    # 5. Choix de push
    print("🌿 Voulez-vous :\n1) Pusher sur main\n2) Créer une branche")
    choice = input("Votre choix (1 ou 2) : ").strip()

    if choice == '1':
        run_command("git branch -M main")
        if not remote_exists():
            remote_url = input("🔗 URL du dépôt distant (GitHub) : ").strip()
            run_command(f"git remote add origin {remote_url}")
        run_command("git push -u origin main")
        print("✅ Poussé sur `main` avec succès.")

    elif choice == '2':
        branch_name = input("🌱 Nom de la branche à créer : ").strip()

        if branch_exists(branch_name):
            print(f"⚠️ La branche `{branch_name}` existe déjà.")
            print("1) Supprimer cette branche")
            print("2) Utiliser cette branche")
            print("3) Annuler")
            branch_choice = input("Votre choix : ").strip()

            if branch_choice == '1':
                delete_branch(branch_name)
                run_command(f"git checkout -b {branch_name}")
            elif branch_choice == '2':
                run_command(f"git checkout {branch_name}")
            else:
                exit()
        else:
            run_command(f"git checkout -b {branch_name}")

        if not remote_exists():
            remote_url = input("🔗 URL du dépôt distant (GitHub) : ").strip()
            run_command(f"git remote add origin {remote_url}")

        confirm_push = input(f"🚀 Pusher sur la branche `{branch_name}` ? (y/n) : ").lower()
        if confirm_push == 'y':
            run_command(f"git push -u origin {branch_name}")
            print(f"✅ Poussé sur la branche `{branch_name}` avec succès.")

    # 6. Menu équipe
    team_collab = input("\n👥 Travailles-tu en équipe ? Accéder au menu collaboration ? (y/n) : ").lower()
    if team_collab == 'y':
        team_menu(repo_path)

if __name__ == "__main__":
    main()
