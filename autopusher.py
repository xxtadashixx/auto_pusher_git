import os
import subprocess

def run_command(command, check=True):
    result = subprocess.run(command, shell=True, text=True)
    if check and result.returncode != 0:
        print("❌ Une erreur est survenue ou aucune mofification sur le code ")
        exit()

def branch_exists(branch_name):
    result = subprocess.run(f"git branch --list {branch_name}", shell=True, text=True, capture_output=True)
    return branch_name in result.stdout

def remote_exists():
    result = subprocess.run("git remote", shell=True, text=True, capture_output=True)
    return 'origin' in result.stdout

def setup_remote(remote_url):
    """Ajoute ou remplace le remote origin avec l'URL donnée"""
    if remote_exists():
        run_command("git remote remove origin")
    run_command(f"git remote add origin {remote_url}")

def delete_branch(branch_name):
    run_command(f"git branch -D {branch_name}")

def list_local_branches():
    result = subprocess.run("git branch", shell=True, text=True, capture_output=True)
    branches = result.stdout.strip().split('\n')
    return [b.strip().replace("* ", "") for b in branches]

def menu_delete_branch():
    branches = list_local_branches()
    print("\n🧹 Liste des branches locales :")
    for i, branch in enumerate(branches):
        print(f"{i + 1}) {branch}")

    try:
        choice = int(input("Sélectionnez le numéro de la branche à supprimer (ou 0 pour annuler) : "))
        if choice == 0:
            print("❌ Suppression annulée")
            return
        selected_branch = branches[choice - 1]

        current_branch_result = subprocess.run("git branch --show-current", shell=True, text=True, capture_output=True)
        current_branch = current_branch_result.stdout.strip()
        if selected_branch == current_branch:
            print("⚠️ la branche est actuellement utilisée donc elle ne peut pas être supprimée")
            return

        confirm = input(f"❓ Supprimer la branche `{selected_branch}` ? (y/n) : ").lower()
        if confirm == 'y':
            delete_branch(selected_branch)
            print(f"✅ Branche `{selected_branch}` supprimée avec succès !")
        else:
            print("❌ Suppression annulée")
    except (ValueError, IndexError):
        print("❌ Entrée invalide.")

def main():
    print("""
    ***************************************
    *  Bienvenue dans AutoPusher v1.0      *
    *  Automatisation des push GitHub      *
    *  par xxtadashixx                     *
    ***************************************
    """)

    repo_path = input("📁 Chemin du dossier à pusher : ").strip()
    os.chdir(repo_path)
    print(f"📂 Répertoire actuel : {os.getcwd()}")

    if not os.path.exists(".git"):
        init = input("🔧 Initialiser un dépôt Git ici ? (y/n) : ").lower()
        if init == 'y':
            run_command("git init")
            print("✅ Dépôt Git initialisé.")
        else:
            print("❌ Opération annulée.")
            return
    else:
        print("✅ Dépôt Git déjà initialisé.")
    specific_path = input("➕ entrez le dossier specifique à pusher ou sinon appuyez sur Entrée pour tout ajouter : ").strip()
    if specific_path:
        run_command(f"git add {specific_path}")
    else:
        run_command("git add .")

    commit_msg = input("📝 Message de commit : ").strip()
    run_command(f'git commit -m "{commit_msg}"')

    print("🌿 Que voulez-vous faire :\n1) Pusher sur main\n2) Créer une branche\n3) Gérer les branches (voir/supprimer)")
    choice = input("entrez votre choix (1 ou 2 ou 3) : ").strip()

    if choice == '1':
        run_command("git branch -M main")
        remote_url = input("🔗 Entrer l'URL du dépôt distant (GitHub) : ").strip()
        setup_remote(remote_url)
        run_command("git push -u origin main")
        print("🚀 Poussé sur `main` avec succès !")

    elif choice == '2':
        branch_name = input("🌱 Nom de la branche à créer : ").strip()

        if branch_exists(branch_name):
            print(f"⚠️ La branche `{branch_name}` existe déjà")
            print("1) Utiliser cette branche\n2) Choisir un autre nom\n3) Annuler")
            branch_choice = input("Votre choix (1/2/3) : ").strip()

            if branch_choice == '1':
                run_command(f"git checkout {branch_name}")
            elif branch_choice == '2':
                branch_name = input("🌱 Nouveau nom de la branche : ").strip()
                run_command(f"git checkout -b {branch_name}")
            elif branch_choice == '3':
                print("⏹️ Opération annulée")
                return
            else:
                print("❌ Choix invalide")
                return
        else:
            run_command(f"git checkout -b {branch_name}")

        remote_url = input("🔗 Entrer l'URL du dépôt distant (GitHub) : ").strip()
        setup_remote(remote_url)

        confirm_push = input(f"🚀 Pusher sur `{branch_name}` ? (y/n) : ").lower()
        if confirm_push == 'y':
            run_command(f"git push -u origin {branch_name}")
            print(f"✅ Poussé sur `{branch_name}` avec succès !")
        else:
            print("❌ Push annulé")

    elif choice == '3':
        menu_delete_branch()

    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    main()
