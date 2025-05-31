import os
import subprocess

def run_command(command):
    """Exécute une commande shell et affiche le résultat."""
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode != 0:
        print("❌ Une erreur est survenue.")
        exit()

def main():
    print("🎉 Bienvenue dans AutoPusher :)")
    
    # 1. Demander le chemin du dossier à pousser
    repo_path = input("📁 Coller votre chemin du dossier à pusher : ").strip()
    os.chdir(repo_path)
    print(f"📂 Répertoire actuel : {os.getcwd()}")

    # 2. Initier un dépôt Git si nécessaire
    init = input("🔧 Voulez-vous initialiser un dépôt Git ici ? (y/n) : ").lower()
    if init == 'y':
        run_command("git init")

    # 3. Ajouter les fichiers
    specific_path = input("➕ Voulez-vous ajouter un dossier/fichier spécifique ? Sinon appuyez sur Entrée pour tout ajouter : ").strip()
    if specific_path:
        run_command(f"git add {specific_path}")
    else:
        run_command("git add .")

    # 4. Message de commit
    commit_msg = input("📝 Entrer un message de commit : ").strip()
    run_command(f'git commit -m "{commit_msg}"')

    # 5. Choisir entre main ou nouvelle branche
    print("🌿 Voulez-vous :")
    print("1) Pusher sur main")
    print("2) Créer une nouvelle branche")
    choice = input("Votre choix (1 ou 2) : ").strip()

    if choice == '1':
        remote_url = input("🔗 Entrer l'URL du dépôt distant (GitHub) : ").strip()
        run_command("git branch -M main")
        run_command(f"git remote add origin {remote_url}")
        run_command("git push -u origin main")
        print("🚀 Poussé sur la branche `main` avec succès !")

    elif choice == '2':
        branch_name = input("🌱 Entrer le nom de la nouvelle branche : ").strip()
        run_command(f"git checkout -b {branch_name}")
        print(f"✅ Branche `{branch_name}` créée.")
        confirm_push = input(f"🚀 Voulez-vous pusher sur la branche `{branch_name}` ? (y/n) : ").lower()
        if confirm_push == 'y':
            remote_url = input("🔗 Entrer l'URL du dépôt distant (GitHub) : ").strip()
            run_command(f"git remote add origin {remote_url}")
            run_command(f"git push -u origin {branch_name}")
            print(f"🎉 Poussé sur la branche `{branch_name}` avec succès !")
        else:
            print("⏹️ Push annulé.")

    else:
        print("❌ Choix invalide. Terminé.")

if __name__ == "__main__":
    main()
