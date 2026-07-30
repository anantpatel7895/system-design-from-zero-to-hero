from app.repository import ProductRepository


class ProductService:

    def __init__(self):

        self.repository = ProductRepository()

    def purchase(
        self,
        db,
        product_id: int,
    ):

        stock = self.repository.get_stock(
            db,
            product_id,
        )

        print(f"Current Stock = {stock}")

        if stock <= 0:

            print("Out Of Stock")

            db.rollback()

            return
        
        input("Press ENTER to BUY...") # will fill payment details

        stock -= 1

        self.repository.update_stock(
            db,
            product_id,
            stock,
        )

        print("Purchased")

        input("Press ENTER to COMMIT...")

        db.commit()

        print("Committed")

    def atomic_purchase(self, db, product_id) -> None:

        stock = self.repository.get_stock_for_update(
            db,
            product_id,
        )

        print(f"Current Stock = {stock}")

        

        if stock <= 0:

            print("Out Of Stock")

            db.rollback()

            return
        
        input("Press ENTER to BUY...") # will fill payment details

        stock -= 1

        self.repository.update_stock(
            db,
            product_id,
            stock,
        )

        print("Purchased")

        input("Press ENTER to COMMIT...")

        db.commit()

        print("Committed")


    