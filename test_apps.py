#!/usr/bin/env python3
"""Test script for application discovery and launching system"""

from jarvis.applications import ApplicationDiscovery, ApplicationLauncher


def test_application_discovery():
    """Test the application discovery system"""
    print("Testing Application Discovery System...")
    print("=" * 50)

    # Initialize discovery
    discovery = ApplicationDiscovery()

    # Get a few applications to test
    apps_dict = discovery.discover_all_applications()
    apps = list(apps_dict.values())
    print(f"\nFound {len(apps)} applications")

    # Show first 10 applications
    print("\nFirst 10 applications found:")
    for i, app in enumerate(apps[:10]):
        print(f"{i+1:2d}. {app.name} - {app.path}")

    return apps


def test_application_launcher(apps):
    """Test the application launcher with fuzzy matching"""
    print("\n" + "=" * 50)
    print("Testing Application Launcher...")

    # Initialize discovery first
    discovery = ApplicationDiscovery()
    launcher = ApplicationLauncher(discovery)

    # Test some common applications
    test_queries = [
        "calculator",
        "notepad",
        "paint",
        "browser",
        "chrome",
        "valorant",
        "val"
    ]

    print("\nTesting fuzzy matching for common applications:")
    for query in test_queries:
        result = launcher.find_application(query)
        if result:
            print(f"\nQuery: '{query}'")
            print(f"Best matches:")
            for i, (app, score) in enumerate(result[:3]):
                print(f"  {i+1}. {app.name} (score: {score})")
        else:
            print(f"\nQuery: '{query}' - No matches found")


def main():
    try:
        # Test discovery
        apps = test_application_discovery()

        # Test launcher
        test_application_launcher(apps)

        print("\n" + "=" * 50)
        print("Application system test completed successfully!")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
