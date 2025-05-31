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

def delete_branch(branch_name):
    result = run_command("git rev-parse --abbrev-ref HEAD", check=False)
    if result is None:
        print("❌ Impossible de récupérer la branche actuelle.")
        return

    current_branch = result.strip()
    if current_branch == branch_name:
        print(f"🔄 Vous êtes actuellement sur la branche `{branch_name}`. Changement temporaire vers `main` pour la suppression.")
        run_command("git checkout main")
    
    run_command(f"git branch -D {branch_name}")
    print(f"✅🗑️ Branche `{branch_name}` supprimée avec succès.")    

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
    print("🌿 Voulez-vous :\n1) Pusher sur main\n2) Créer une branche")
    choice = input("Votre choix (1 ou 2) : ").strip()

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

        # Vérifie si la branche existe déjà
        if branch_exists(branch_name):
            print(f"⚠️ La branche `{branch_name}` existe déjà.")
            print("Que voulez-vous faire ?")
            print("1) Supprimer cette branche")
            print("2) Utiliser cette branche")
            print("3) Annuler")
            branch_choice = input("Votre choix (1/2/3) : ").strip()

            if branch_choice == '1':
                delete_branch(branch_name)
                run_command(f"git checkout -b {branch_name}")
            elif branch_choice == '2':
                run_command(f"git checkout {branch_name}")
            else:
                print("⏹️ Opération annulée.")
                exit()
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
    else:
        print("❌ Choix invalide.")

if __name__ == "__main__":
    main()
