import importlib.util
import pathlib
import sys

#I had troubles with using the 'from main import normalize_pair' so I used the dynamic import method instead
ROOT = pathlib.Path(__file__).resolve().parents[1]

main_path = ROOT / "main.py"

spec = importlib.util.spec_from_file_location("main", main_path)
main = importlib.util.module_from_spec(spec)
sys.modules["main"] = main
spec.loader.exec_module(main)

normalize_pair = main.normalize_pair

def normalize_pair_trims_and_lowercase():
    #this function tests if the normalize_pair function trims spaces and lowercases the input of the user
    a, b = ("  Aspirin  ", "IBUPROFEN")
    assert a == "aspirin"
    assert b == "ibuprofen"
    
def test_normalize_pair_is_order_independent():
    #this one checks if the order doesn't matter, because after applying the normalize_pair function the tuple should be the same
    p1 = normalize_pair("Aspirin", "Ibuprofen")
    p2 = normalize_pair("Ibuprofen", "Aspirin")
    assert p1 == p2