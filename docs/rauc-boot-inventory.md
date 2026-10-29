
# SecureEdge - Inventaire du démarrage PROD

## Plateforme

- Raspberry Pi Zero 2 W
- Architecture ARM64
- Yocto Scarthgap
- Stockage : microSD unique

## Organisation actuelle

### Partition Boot

- Périphérique : /dev/mmcblk0p1
- Système de fichiers : FAT
- Montage : /boot
- Début : secteur 8192
- Taille : 266240 secteurs, soit 130 MiB

### Partition RootFS

- Périphérique : /dev/mmcblk0p2
- Système de fichiers : ext4
- Montage : /
- Début : secteur 278528
- Taille : 436632 secteurs, soit environ 213,2 MiB

## Paramètres du noyau

root=/dev/mmcblk0p2
rootfstype=ext4
rootwait
net.ifnames=0

## Conclusion

Le système PROD actuel utilise une seule
partition racine.

Pour RAUC, une nouvelle image WIC devra
permettre la sélection de deux systèmes A/B.

## Architecture OTA envisagée

- Sélection du boot via firmware Raspberry Pi
- Boot A et Boot B
- RootFS A et RootFS B
- Partition DATA persistante
- Installation et vérification des bundles RAUC
- Mécanisme de confirmation et rollback

## Travaux restant à valider

- Contenu complet de /boot
- Support opérationnel de tryboot
- Format de la table de partitions
- Intégration RAUC avec le firmware
- Préservation des certificats et du Wi-Fi
- Watchdog et retour après échec
