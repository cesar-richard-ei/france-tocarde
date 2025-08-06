#!/bin/bash
# Script pour exécuter les tests avec couverture de code

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}>>> Exécution des tests avec couverture de code${NC}"

# Vérification des arguments
COVERAGE_OPTS=""
if [ "$1" == "--html" ] || [ "$2" == "--html" ]; then
    COVERAGE_OPTS="$COVERAGE_OPTS --html"
fi

if [ "$1" == "--xml" ] || [ "$2" == "--xml" ]; then
    COVERAGE_OPTS="$COVERAGE_OPTS --xml"
fi

# Exécution des tests avec la couverture
python manage.py test --with-coverage $COVERAGE_OPTS $@

# Vérification du résultat
TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}>>> Tests réussis !${NC}"
else
    echo -e "${RED}>>> Tests échoués avec code $TEST_RESULT${NC}"
fi

# Afficher l'emplacement des rapports si générés
if [ "$1" == "--html" ] || [ "$2" == "--html" ]; then
    echo -e "${YELLOW}>>> Rapport HTML généré dans coverage_reports/html/index.html${NC}"
fi

if [ "$1" == "--xml" ] || [ "$2" == "--xml" ]; then
    echo -e "${YELLOW}>>> Rapport XML généré dans coverage_reports/coverage.xml${NC}"
fi

exit $TEST_RESULT
