/**
 * Tests unitaires pour la validation des noms/prénoms
 */

import { describe, it, expect } from 'vitest';
import { validateName } from './validations';

describe('validateName', () => {
  describe('Cas valides', () => {
    it('devrait accepter un nom simple', () => {
      const result = validateName('Dupont', 'Nom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });

    it('devrait accepter un prénom simple', () => {
      const result = validateName('Jean', 'Prénom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });

    it('devrait accepter un nom avec un tiret', () => {
      const result = validateName('Jean-Claude', 'Prénom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });

    it('devrait accepter un nom avec une apostrophe', () => {
      const result = validateName("O'Connor", 'Nom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });

    it('devrait accepter un nom avec des espaces', () => {
      const result = validateName('Marie Anne', 'Prénom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });

    it('devrait accepter un nom avec des accents', () => {
      const result = validateName('François', 'Prénom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });

    it('devrait accepter un nom avec des caractères spéciaux français', () => {
      const result = validateName('Müller', 'Nom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });
  });

  describe('Cas invalides - chiffres', () => {
    it('devrait rejeter un nom contenant des chiffres', () => {
      const result = validateName('Dupont123', 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom ne doit pas contenir de chiffres.');
    });

    it('devrait rejeter un prénom contenant des chiffres', () => {
      const result = validateName('Jean123', 'Prénom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Prénom ne doit pas contenir de chiffres.');
    });

    it('devrait rejeter un nom qui est juste un chiffre', () => {
      const result = validateName('123', 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom ne doit pas contenir de chiffres.');
    });

    it('devrait rejeter un nom avec des chiffres au milieu', () => {
      const result = validateName('Du99pont', 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom ne doit pas contenir de chiffres.');
    });
  });

  describe('Cas invalides - longueur', () => {
    it('devrait rejeter un nom trop court (1 caractère)', () => {
      const result = validateName('J', 'Prénom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Prénom trop court (minimum 2 caractères).');
    });

    it('devrait rejeter un nom vide', () => {
      const result = validateName('', 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom requis.');
    });

    it('devrait rejeter un nom avec seulement des espaces', () => {
      const result = validateName('   ', 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom trop court (minimum 2 caractères).');
    });

    it('devrait rejeter un nom trop long (> 100 caractères)', () => {
      const longName = 'a'.repeat(101);
      const result = validateName(longName, 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom trop long (maximum 100 caractères).');
    });
  });

  describe('Cas invalides - caractères spéciaux', () => {
    it('devrait rejeter un nom avec des caractères spéciaux interdits (@)', () => {
      const result = validateName('Dupont@', 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom invalide : lettres, espaces, apostrophes et tirets uniquement.');
    });

    it('devrait rejeter un nom avec des symboles (#)', () => {
      const result = validateName('Jean#', 'Prénom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Prénom invalide : lettres, espaces, apostrophes et tirets uniquement.');
    });

    it('devrait rejeter un nom avec des parenthèses', () => {
      const result = validateName('Dupont(test)', 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom invalide : lettres, espaces, apostrophes et tirets uniquement.');
    });
  });

  describe('Cas limites', () => {
    it('devrait accepter un nom de 2 caractères', () => {
      const result = validateName('Le', 'Nom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });

    it('devrait accepter un nom de 100 caractères', () => {
      const longName = 'a'.repeat(100);
      const result = validateName(longName, 'Nom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });

    it('devrait trim les espaces avant et après', () => {
      const result = validateName('  Jean  ', 'Prénom');
      expect(result.valid).toBe(true);
      expect(result.error).toBeNull();
    });
  });

  describe('Cas de types invalides', () => {
    it('devrait rejeter null', () => {
      const result = validateName(null, 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom requis.');
    });

    it('devrait rejeter undefined', () => {
      const result = validateName(undefined, 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom requis.');
    });

    it('devrait rejeter un nombre', () => {
      const result = validateName(123, 'Nom');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Nom requis.');
    });
  });
});
