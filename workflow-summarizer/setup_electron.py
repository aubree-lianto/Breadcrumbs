import sys
sys.path.insert(0, '.')

from electron_launcher import list_electron_apps, launch_with_debug


def main():
    print("=== Electron App Setup for Breadcrumbs ===\n")

    apps = list_electron_apps()

    print("Detected Electron apps:\n")
    for i, app in enumerate(apps):
        status = "✓ RUNNING" if app["running"] else "  stopped"
        found = "found" if app["found"] else "NOT FOUND"
        print(f"  [{i+1}] {app['app']}: {status} ({found})")
        if app["found"]:
            print(f"      Debug port: {app['port']}")

    print("\nOptions:")
    print("  [number] - Launch that app with debug enabled")
    print("  [a]      - Launch all found apps with debug enabled")
    print("  [q]      - Quit")

    choice = input("\nChoice: ").strip().lower()

    if choice == 'q':
        return

    if choice == 'a':
        for app in apps:
            if app["found"]:
                result = launch_with_debug(app["key"])
                print(f"  {app['app']}: {result}")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(apps):
                app = apps[idx]
                if app["found"]:
                    result = launch_with_debug(app["key"])
                    print(f"\n{result}")
                else:
                    print(f"\n{app['app']} not found on this system")
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid choice")


if __name__ == "__main__":
    main()
