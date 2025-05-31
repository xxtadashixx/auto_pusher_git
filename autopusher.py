import os
import subprocess

def run_command(command, check=True):
    """Exécute une commande shell et affiche les erreurs si besoin."""
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

def list_local_branches():
    """Liste toutes les branches locales."""
    result = subprocess.run("git branch", shell=True, text=True, capture_output=True)
    branches = result.stdout.strip().split('\n')
    return [b.strip().replace("* ", "") for b in branches]

def menu_delete_branch():
    """Menu pour afficher et supprimer une branche locale."""
    branches = list_local_branches()
    print("\n🧹 Liste des branches locales :")
    for i, branch in enumerate(branches):
        print(f"{i + 1}) {branch}")

    try:
        choice = int(input("Sélectionnez le numéro de la branche à supprimer (ou 0 pour annuler) : "))
        if choice == 0:
            print("❌ Suppression annulée.")
            return
        selected_branch = branches[choice - 1]

        # Ne pas supprimer la branche actuellement utilisée
        current_branch_result = subprocess.run("git branch --show-current", shell=True, text=True, capture_output=True)
        current_branch = current_branch_result.stdout.strip()
        if selected_branch == current_branch:
            print("⚠️ Vous ne pouvez pas supprimer la branche actuellement utilisée.")
            return

        confirm = input(f"❓ Êtes-vous sûr de vouloir supprimer la branche `{selected_branch}` ? (y/n) : ").lower()
        if confirm == 'y':
            delete_branch(selected_branch)
            print(f"✅ Branche `{selected_branch}` supprimée.")
        else:
            print("❌ Suppression annulée.")
    except (ValueError, IndexError):
        print("❌ Entrée invalide.")

def main():
    print("🎉 Bienvenue dans AutoPusher :)")

    # 1. Choisir le dossier
    repo_path = input("📁 Coller le chemin du dossier à pusher : ").strip()
    os.chdir(repo_path)
    print(f"📂 Répertoire actuel : {os.getcwd()}")

    # 2. Initialiser si besoin
    if not os.path.exists(".git"):
        init = input("🔧 Voulez-vous initialiser un dépôt Git ici ? (y/n) : ").lower()
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
    print("🌿 Que voulez-vous faire :\n1) Pusher sur main\n2) Créer une branche\n3) Gérer les branches (voir/supprimer)")
    choice = input("Votre choix (1, 2 ou 3) : ").strip()

    if choice == '1':
        # Branch main
        run_command("git branch -M main")
        if not remote_exists():
            remote_url = input("🔗 Entrer l'URL du dépôt distant (GitHub) : ").strip()
            run_command(f"git remote add origin {remote_url}")
        run_command("git push -u origin main")
        print("🚀 Poussé sur la branche `main` avec succès !")

    elif choice == '2':
        branch_name = input("🌱 Nom de la branche à créer : ").strip()

        if branch_exists(branch_name):
            print(f"⚠️ La branche `{branch_name}` existe déjà.")
            print("Que voulez-vous faire ?")
            print("1) Utiliser cette branche")
            print("2) Choisir un autre nom")
            print("3) Annuler")
            branch_choice = input("Votre choix (1/2/3) : ").strip()

            if branch_choice == '1':
                run_command(f"git checkout {branch_name}")
            elif branch_choice == '2':
                branch_name = input("🌱 Nouveau nom de la branche : ").strip()
                run_command(f"git checkout -b {branch_name}")
            elif branch_choice == '3':
                print("⏹️ Opération annulée.")
                return
            else:
                print("❌ Choix invalide, opération annulée.")
                return
        else:
            run_command(f"git checkout -b {branch_name}")

        # Push de la branche
        if not remote_exists():
            remote_url = input("🔗 Entrer l'URL du dépôt distant (GitHub) : ").strip()
            run_command(f"git remote add origin {remote_url}")

        confirm_push = input(f"🚀 Pusher sur la branche `{branch_name}` ? (y/n) : ").lower()
        if confirm_push == 'y':
            run_command(f"git push -u origin {branch_name}")
            print(f"✅ Poussé sur la branche `{branch_name}` avec succès !")
        else:
            print("❌ Push annulé.")

    elif choice == '3':
        menu_delete_branch()

    else:
        print("❌ Choix invalide.")

if __name__ == "__main__":
    main()
