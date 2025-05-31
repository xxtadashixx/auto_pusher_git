import os
import subprocess
from pathlib import Path

def run_command(command, check=True, cwd=None):
    """Exécute une commande shell et gère les erreurs"""
    try:
        result = subprocess.run(command, shell=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              cwd=cwd)
        if check and result.returncode != 0:
            print(f"❌ Erreur: {result.stderr.strip()}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def branch_exists(branch_name, repo_path):
    """Vérifie si une branche existe localement"""
    branches = run_command("git branch --list", cwd=repo_path)
    return branches and branch_name in branches.split("\n")

def remote_exists(repo_path):
    """Vérifie si le remote origin est configuré"""
    remotes = run_command("git remote", cwd=repo_path)
    return remotes and "origin" in remotes.split("\n")

def get_current_branch(repo_path):
    """Récupère la branche actuelle"""
    return run_command("git branch --show-current", cwd=repo_path)

def switch_to_main_branch(repo_path):
    """Bascule vers la branche main/master ou en crée une si nécessaire"""
    # Vérifie d'abord si main existe
    if run_command("git show-ref --verify refs/heads/main", cwd=repo_path, check=False):
        return run_command("git checkout main", cwd=repo_path) is not None
    
    # Sinon vérifie master
    if run_command("git show-ref --verify refs/heads/master", cwd=repo_path, check=False):
        return run_command("git checkout master", cwd=repo_path) is not None
    
    # Sinon crée main
    print("ℹ️ Création de la branche main...")
    if (run_command("git checkout --orphan main", cwd=repo_path) is not None and
        run_command("git rm -rf .", cwd=repo_path, check=False) is not None and
        run_command("git commit --allow-empty -m 'Initial commit'", cwd=repo_path) is not None):
        return True
    
    return False

def delete_branch(branch_name, repo_path):
    """Supprime une branche locale de manière sécurisée"""
    current_branch = get_current_branch(repo_path)
    if current_branch is None:
        return False
    
    if current_branch == branch_name:
        print(f"⚠️ Vous êtes sur la branche à supprimer. Basculement vers main...")
        if not switch_to_main_branch(repo_path):
            return False
    
    if run_command(f"git branch -D {branch_name}", cwd=repo_path) is None:
        return False
    
    print(f"✅ Branche '{branch_name}' supprimée")
    return True

def initialize_repo(repo_path):
    """Initialise un nouveau dépôt Git"""
    if run_command("git init", cwd=repo_path) is None:
        return False
    
    # Crée un premier commit vide
    os.chdir(repo_path)
    with open("README.md", "w") as f:
        f.write("# Nouveau projet\n")
    
    if (run_command("git add README.md", cwd=repo_path) is not None and
        run_command("git commit -m 'Initial commit'", cwd=repo_path) is not None):
        return True
    return False

def add_files(repo_path):
    """Gère l'ajout des fichiers au staging"""
    specific_path = input("➕ Chemin spécifique (ou Entrée pour tout ajouter) : ").strip()
    if specific_path:
        full_path = os.path.join(repo_path, specific_path)
        if not os.path.exists(full_path):
            print(f"❌ Chemin invalide: {specific_path}")
            return False
        return run_command(f"git add {specific_path}", cwd=repo_path) is not None
    else:
        return run_command("git add .", cwd=repo_path) is not None

def create_commit(repo_path):
    """Crée un nouveau commit"""
    while True:
        commit_msg = input("📝 Message de commit : ").strip()
        if commit_msg:
            break
        print("❌ Le message ne peut pas être vide")
    
    return run_command(f'git commit -m "{commit_msg}"', cwd=repo_path) is not None

def push_to_main(repo_path):
    """Pousse les changements sur la branche main"""
    # Force la branche main si elle n'existe pas
    if not branch_exists("main", repo_path):
        run_command("git branch -M main", cwd=repo_path)
    
    if not remote_exists(repo_path):
        remote_url = input("🔗 URL du dépôt distant : ").strip()
        if not remote_url.startswith(("http", "git@")):
            print("❌ URL invalide. Doit commencer par http://, https:// ou git@")
            return False
        if run_command(f"git remote add origin {remote_url}", cwd=repo_path) is None:
            return False
    
    return run_command("git push -u origin main", cwd=repo_path) is not None

def handle_existing_branch(branch_name, repo_path):
    """Gère le cas où la branche existe déjà"""
    print(f"⚠️ La branche '{branch_name}' existe déjà.")
    print("1) Supprimer et recréer\n2) Utiliser cette branche\n3) Annuler")
    
    while True:
        choice = input("Choix (1/2/3) : ").strip()
        if choice == "1":
            if not delete_branch(branch_name, repo_path):
                return False
            return run_command(f"git checkout -b {branch_name}", cwd=repo_path) is not None
        elif choice == "2":
            return run_command(f"git checkout {branch_name}", cwd=repo_path) is not None
        elif choice == "3":
            return None  # Signale l'annulation
        print("❌ Choix invalide")

def push_to_new_branch(repo_path):
    """Pousse les changements sur une nouvelle branche"""
    while True:
        branch_name = input("🌱 Nom de la nouvelle branche : ").strip()
        if branch_name:
            break
        print("❌ Le nom ne peut pas être vide")
    
    # Gestion de la branche existante
    if branch_exists(branch_name, repo_path):
        result = handle_existing_branch(branch_name, repo_path)
        if result is None:  # Annulation
            return False
        if not result:  # Échec
            return False
    else:
        if run_command(f"git checkout -b {branch_name}", cwd=repo_path) is None:
            return False
    
    # Configuration du remote si nécessaire
    if not remote_exists(repo_path):
        remote_url = input("🔗 URL du dépôt distant : ").strip()
        if not remote_url.startswith(("http", "git@")):
            print("❌ URL invalide")
            return False
        if run_command(f"git remote add origin {remote_url}", cwd=repo_path) is None:
            return False
    
    # Confirmation du push
    confirm = input(f"🚀 Pousser sur '{branch_name}' ? (o/n) : ").lower()
    if confirm != 'o':
        print("⏹️ Push annulé")
        return True  # Considéré comme succès sans push
    
    return run_command(f"git push -u origin {branch_name}", cwd=repo_path) is not None

def main():
    print("\n🎉 Bienvenue dans AutoPusher v2.0 🚀\n")

    # 1. Sélection du répertoire
    while True:
        repo_path = input("📁 Chemin du dossier : ").strip()
        if os.path.isdir(repo_path):
            break
        print("❌ Dossier introuvable")
    
    try:
        repo_path = os.path.abspath(repo_path)
        os.chdir(repo_path)
        print(f"📂 Dossier : {repo_path}")
    except Exception as e:
        print(f"❌ Erreur d'accès : {e}")
        return

    # 2. Initialisation Git si nécessaire
    if not os.path.exists(os.path.join(repo_path, ".git")):
        if input("🔧 Initialiser un dépôt Git ? (o/n) : ").lower() == 'o':
            if not initialize_repo(repo_path):
                print("❌ Échec de l'initialisation")
                return
            print("✅ Dépôt initialisé")
        else:
            print("❌ Ce n'est pas un dépôt Git")
            return

    # 3. Ajout des fichiers
    if not add_files(repo_path):
        print("❌ Échec de l'ajout des fichiers")
        return

    # 4. Création du commit
    if not create_commit(repo_path):
        print("❌ Échec du commit")
        return

    # 5. Choix du push
    print("\n🌿 Options de push :")
    print("1) Pusher sur main")
    print("2) Créer une nouvelle branche")
    
    while True:
        choice = input("Votre choix (1/2) : ").strip()
        if choice in ("1", "2"):
            break
        print("❌ Choix invalide")
    
    success = False
    if choice == "1":
        success = push_to_main(repo_path)
        if success:
            print("\n✅ Push sur main réussi!")
    else:
        success = push_to_new_branch(repo_path)
        if success:
            print("\n✅ Push sur la nouvelle branche réussi!")
    
    if not success:
        print("\n❌ Échec de l'opération")
    else:
        print("\n🎉 Opération terminée avec succès!")

if __name__ == "__main__":
    main()