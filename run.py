import traceback
try:
    import main
    main.main()
except Exception as e:
    with open('crash.log', 'w') as f:
        traceback.print_exc(file=f)
