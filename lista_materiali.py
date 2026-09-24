import pyroomacoustics as pra

def mostra_materiali():
    # Accediamo al dizionario interno dei materiali della libreria
    database = pra.parameters.materials_absorption_table
    
    print(f"Trovati {len(database)} materiali integrati in questa versione:\n")
    
    # Stampiamo l'elenco in ordine alfabetico
    for materiale in sorted(database.keys()):
        print(f"- {materiale}")

if __name__ == "__main__":
    mostra_materiali()