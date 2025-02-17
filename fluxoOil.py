import math

class FluxoOilCalculator:
    def __init__(self, ko: float, h: float, pr: float, pw: float, Bo: float, uo: float, re: float, rw: float):
        self.ko = ko
        self.h = h
        self.pr = pr
        self.pw = pw
        self.uo = uo
        self.Bo = Bo
        self.re = re
        self.rw = rw

    def calcular_qo(self) -> float:
        """
        Calcula o valor de qo baseado na fórmula:
        qo = (0.00708 * ko * h * (pr - pw)) / (uoBo * ln(0.472 * re / rw))
        """
        try:
            denominador = self.uo * self.Bo * math.log(0.472 * self.re / self.rw)
            if denominador == 0:
                raise ValueError("Denominador igual a zero, verifique os valores inseridos.")
            return (0.00708 * self.ko * self.h * (self.pr - self.pw)) / denominador
        except ValueError as ve:
            raise ve

def main():
    print("=== Cálculo de Qo ===")
    try:
        ko = float(input("Informe o valor de ko: "))
        h = float(input("Informe o valor de h: "))
        pr = float(input("Informe o valor de pr: "))
        pw = float(input("Informe o valor de pw: "))
        uo = float(input("Informe o valor de uo: "))
        Bo = float(input("Informe o valor de Bo: "))
        re = float(input("Informe o valor de re: "))
        rw = float(input("Informe o valor de rw: "))

        calculadora = FluxoOilCalculator(ko, h, pr, pw, uo, Bo, re, rw)
        resultado = calculadora.calcular_qo()
        print(f"\nO valor calculado de qo é: {resultado}")
    except Exception as e:
        print(f"Erro ao calcular qo: {e}")

if __name__ == "__main__":
    main()