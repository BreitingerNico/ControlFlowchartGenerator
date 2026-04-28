"""
example code to test the control flowchart generator 
with various constructs like loops, conditionals, try-except, and more. (AI-generated)
"""

def komplexer_test_lauf(werte_liste):
    ergebnis = 0
    zaehler = 0
    
    # 1. Standard-Schleife mit Verzweigung
    for wert in werte_liste:
        print(f"Prüfe Wert: {wert}")
        
        if wert is None:
            print("Überspringe None")
            continue  # Testet Rücksprung zum Schleifenkopf
            
        # 2. Verschachtelte Logik und Try-Block
        try:
            if wert == "STOP":
                print("Abbruchsignal erhalten")
                break  # Testet Sprung aus der Schleife zum Finally/Exit
            
            # Mathematische Operation für AugAssign Test (+=)
            if wert > 0:
                ergebnis += wert
                print("Positiver Wert addiert")
            elif wert < 0:
                ergebnis -= abs(wert)
                print("Negativer Wert subtrahiert")
            else:
                # Testet Division durch Null Exception
                temp = 10 / wert
                
        except ZeroDivisionError:
            print("Fehler: Division durch Null!")
            
        except TypeError as e:
            print(f"Typfehler aufgetreten: {e}")
            
        finally:
            # Dieser Block wird fast immer ausgeführt
            zaehler += 1
            print(f"Durchgang {zaehler} beendet")

    # 3. Abschluss-Logik
    if ergebnis > 100:
        final_status = "Hoch"
    else:
        final_status = "Niedrig"
        
    return f"Status: {final_status}, Gesamt: {ergebnis}"

daten = [10, 0, None, -5, "STOP", 20]
print(komplexer_test_lauf(daten))