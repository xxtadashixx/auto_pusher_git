import os
import subprocess
from pathlib import Path

def run_command(command, check=True, cwd=None):
    """Exécute une commande shell et affiche les erreurs si besoin."""
    result = subprocess.run(command, shell=True, text=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    if check and result.returncode != 0:
        print(f"❌ Erreur: {result.stderr}")
        return None
    return result.stdout

def branch_exists(branch_name, repo_path):
    """Vérifie si une branche locale existe."""
    result = subprocess.run(f"git branch --list {branch_name}", shell=True, 
                          text=True, capture_output=True, cwd=repo_path)
    return branch_name in result.stdout

def remote_exists(repo_path):
    """Vérifie si un remote 'origin' est déjà configuré."""
    result = subprocess.run("git remote", shell=True, 
                          text=True, capture_output=True, cwd=repo_path)
    return 'origin' in result.stdout

def delete_branch(branch_name, repo_path):
    """Supprime une branche locale de manière sécurisée."""
    # Vérifie la branche actuelle
    current_branch = run_command("git branch --show-current", cwd=repo_path)
    if current_branch is None:
        print("❌ Impossible de déterminer la branche actuelle")
        return False
    
    current_branch = current_branch.strip()
    
    # Si on est sur la branche à supprimer, on se déplace d'abord
    if current_branch == branch_name:
        print(f"⚠️ Vous êtes sur la branche à supprimer. Changement vers 'main' temporairement...")
        if run_command("git checkout main", cwd=repo_path) is None:
            return False
    
    # Suppression de la branche
    if run_command(f"git branch -D {branch_name}", cwd=repo_path) is None:
        return False
    
    print(f"✅ Branche '{branch_name}' supprimée avec succès")
    return True

def main():
    print("🎉 Bienvenue dans AutoPusher :)")

    # 1. Choisir le dossier
    while True:
        repo_path = input("📁 Coller le chemin du dossier à pusher : ").strip()
        if not os.path.exists(repo_path):
            print("❌ Chemin invalide. Veuillez réessayer.")
            continue
        break
    
    try:
        os.chdir(repo_path)
        repo_path = os.getcwd()  # Normalise le chemin
        print(f"📂 Répertoire actuel : {repo_path}")
    except Exception as e:
        print(f"❌ Impossible d'accéder au répertoire: {e}")
        exit()

    # 2. Initialiser si besoin
    if not os.path.exists(os.path.join(repo_path, ".git")):
        init = input("🔧 Voulez-vous initialiser un dépôt Git ici ? (y/n) : ").lower()
        if init == 'y':
            if run_command("git init", cwd=repo_path) is None:
                exit()

    # 3. Ajouter fichiers
    specific_path = input("➕ Ajouter un fichier/dossier spécifique ? Sinon Entrée pour tout ajouter : ").strip()
    if specific_path:
        full_path = os.path.join(repo_path, specific_path)
        if not os.path.exists(full_path):
            print(f"❌ Le chemin '{specific_path}' n'existe pas")
            exit()
        if run_command(f"git add {specific_path}", cwd=repo_path) is None:
            exit()
    else:
        if run_command("git add .", cwd=repo_path) is None:
            exit()

    # 4. Commit
    commit_msg = input("📝 Message de commit : ").strip()
    if not commit_msg:
        print("❌ Le message de commit ne peut pas être vide")
        exit()
    
    if run_command(f'git commit -m "{commit_msg}"', cwd=repo_path) is None:
        exit()

    # 5. Choix de push
    print("🌿 Voulez-vous :\n1) Pusher sur main\n2) Créer une branche")
    while True:
        choice = input("Votre choix (1 ou 2) : ").strip()
        if choice in ('1', '2'):
            break
        print("❌ Choix invalide. Veuillez entrer 1 ou 2")

    if choice == '1':
        # Branch main
        if run_command("git branch -M main", cwd=repo_path) is None:
            exit()
            
        if not remote_exists(repo_path):
            remote_url = input("🔗 Entrer l'URL du dépôt distant (GitHub) : ").strip()
            if run_command(f"git remote add origin {remote_url}", cwd=repo_path) is None:
                exit()
        
        if run_command("git push -u origin main", cwd=repo_path) is not None:
            print("🚀 Poussé sur la branche `main` avec succès !")

    elif choice == '2':
        while True:
            branch_name = input("🌱 Nom de la branche à créer : ").strip()
            if branch_name:
                break
            print("❌ Le nom de branche ne peut pas être vide")

        # Vérifie si la branche existe déjà
        if branch_exists(branch_name, repo_path):
            print(f"⚠️ La branche '{branch_name}' existe déjà.")
            print("Que voulez-vous faire ?")
            print("1) Supprimer cette branche et en créer une nouvelle")
            print("2) Utiliser cette branche existante")
            print("3) Annuler")
            
            while True:
                branch_choice = input("Votre choix (1/2/3) : ").strip()
                if branch_choice in ('1', '2', '3'):
                    break
                print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3")

            if branch_choice == '1':
                if not delete_branch(branch_name, repo_path):
                    exit()
                if run_command(f"git checkout -b {branch_name}", cwd=repo_path) is None:
                    exit()
            elif branch_choice == '2':
                if run_command(f"git checkout {branch_name}", cwd=repo_path) is None:
                    exit()
            else:
                print("⏹️ Opération annulée.")
                exit()
        else:
            if run_command(f"git checkout -b {branch_name}", cwd=repo_path) is None:
                exit()

        # Push de la branche
        if not remote_exists(repo_path):
            remote_url = input("🔗 Entrer l'URL du dépôt distant (GitHub) : ").strip()
            if run_command(f"git remote add origin {remote_url}", cwd=repo_path) is None:
                exit()

        confirm_push = input(f"🚀 Pusher sur la branche '{branch_name}' ? (y/n) : ").lower()
        if confirm_push == 'y':
            if run_command(f"git push -u origin {branch_name}", cwd=repo_path) is not None:
                print(f"✅ Poussé sur la branche '{branch_name}' avec succès !")

if __name__ == "__main__":
    main()