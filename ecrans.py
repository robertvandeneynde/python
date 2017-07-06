#! /usr/bin/python3

from fractions import Fraction
from math import sqrt

def affichage(diag, reso_w, reso_h):
    rapport = reso_w / reso_h
    H = diag / sqrt(1 + rapport ** 2)
    W = rapport * H
    ppi = sqrt(reso_w ** 2 + reso_h ** 2) / diag
    ppi2 = (reso_w * reso_h) / (H * W)
    CM_IN = 2.54

    noms = {
        (320,240):"QVGA",
        (640,480):"VGA",
        (768,576):"PAL",
        (800,600):"SVGA",
        (1024,768):"XGA",
        (1400,1050):"SXGA",
        (1600,1200):"UXGA",
        (2048,1536):"QXGA",
        (854,480):"WVGA (SD 480)",
        (960,540):"qHD",
        (1280,720):"HD",
        (1600,900):"HD+",
        (1920,1080):"Full HD",
        (320,200):"CGA",
        (1280,800):"WXGA",
        (1680,1050):"WSXGA+",
        (1920,1200):"WUXGA"
    }

    cutename = noms.get((reso_w,reso_h),'')
    
    ratios_brut = {
        (1366, 768): (16,9)
    }
    
    ratios = {
        (8,5):(16,10)
    }

    frac = Fraction(reso_w,reso_h)
    reduit = ratios_brut.get((reso_w,reso_h)) or (frac.numerator,frac.denominator)
    ratio = ratios.get(reduit,reduit)
    r1,r2 = ratio

    print(
        "          Dimensions: {:.1f}cm x {:.1f}cm ({:.1f}'' x {:.1f}'')"
        .format(W * CM_IN, H * CM_IN, W, H),
        "           Diagonale: {:.1f}cm ({:.1f}'')"
        .format(diag * CM_IN, diag),
        "               Ratio: {}:{} ({:.3f})"
        .format(r1, r2, rapport),
        "      Résolution max: {}x{} ({})"
        .format(reso_w, reso_h, cutename),
        "    Nombre de Pixels: {:.2f} Mega Pixels"
        .format(reso_w * reso_h * 1e-6),
        " Précision diagonale: {:.0f} ppcm ({:.1f} ppi)"
        .format(ppi / CM_IN, ppi),
        "  Largeur d'un pixel: {:.3f} mm"
        .format(W * CM_IN * 10 / reso_w),
        # "Précision de surface: {:.0f} px / cm² ({:.1f} px / in²)"
        # .format(ppi2 / (CM_IN ** 2), ppi2),
        # "   Taille d'un pixel: {:.4f} mm²"
        # .format(1 / ppi2 * (CM_IN ** 2) * 100),
        sep='\n'
    )

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Affiche des informations sur les écrans et les résolutions d'écran")

    parser.add_argument('diagonales_pouces', type=float)
    parser.add_argument('reso_max_largeur', type=int)
    parser.add_argument('reso_max_hauteur', type=int)

    args = parser.parse_args()

    affichage(args.diagonales_pouces, args.reso_max_largeur, args.reso_max_hauteur)
