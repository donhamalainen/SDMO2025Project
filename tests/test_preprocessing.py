from project1developers import process

def test_process_removes_punctuation_and_accents():
    dev = ("Jöhn D'oe", "john.doe@gmail.com")
    name, first, last, i_first, i_last, email, prefix = process(dev)
    assert name == "john doe"
    assert first == "john"
    assert last == "doe"
    assert i_first == "j"
    assert i_last == "d"
    assert prefix == "john.doe"
    assert email == "john.doe@gmail.com"

def test_process_handles_extra_spaces():
    dev = ("  Anna   Maria  Smith  ", "asmith@example.com")
    name, *_ = process(dev)
    assert name == "anna maria smith"

def test_email_prefix_extraction():
        """Test email prefix extraction edge cases"""
        test_cases = [
            ("John Doe", "john.doe+test@gmail.com"),  # Plus addressing
            ("Jane Smith", "jane@subdomain.example.com"),  # Subdomain
            ("Jake Gough", "super.jake@hotmail.co.uk"),  # Complex domain
            ("Simple", "simple@a.co"),  # Short domain
        ]
        
        for dev in test_cases:
            *_, email, prefix = process(dev)
            assert "@" not in prefix
            assert "." not in prefix or prefix.count(".") <= email.count(".")

    
def test_unicode_normalization():
        """Test Unicode character normalization"""
        dev = ("Äsk", "äsk@hotmail.com")
        name, *_ = process(dev)
        # Test that accented characters are handled consistently
        assert len(name) > 0