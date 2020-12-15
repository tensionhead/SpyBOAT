from dataclasses import dataclass

@dataclass
class FrameData:
    """Class for keeping track of finding the optimal path(s)
    through a phase field."""
    
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand
