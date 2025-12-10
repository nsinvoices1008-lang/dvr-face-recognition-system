#!/bin/bash

echo "╔═══════════════════════════════════════════════════╗"
echo "║   DVR Face Recognition - Bootable USB Creator     ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (sudo ./setup-pendrive.sh)"
    exit 1
fi

# Check if device is provided
if [ -z "$1" ]; then
    echo "❌ No device specified"
    echo ""
    echo "Usage: sudo ./setup-pendrive.sh /dev/sdX"
    echo ""
    echo "Available devices:"
    lsblk -d -o NAME,SIZE,TYPE | grep disk
    echo ""
    exit 1
fi

DEVICE=$1

# Confirm device
echo "⚠️  WARNING: This will erase all data on $DEVICE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "📦 Installing required packages..."

apt-get update
apt-get install -y debootstrap grub-pc-bin grub-efi-amd64-bin

echo "✓ Packages installed"
echo ""

echo "💾 Partitioning USB drive..."

# Unmount if mounted
umount ${DEVICE}* 2>/dev/null

# Create partition table
parted -s $DEVICE mklabel gpt
parted -s $DEVICE mkpart primary fat32 1MiB 512MiB
parted -s $DEVICE set 1 esp on
parted -s $DEVICE mkpart primary ext4 512MiB 100%

# Format partitions
mkfs.vfat -F32 ${DEVICE}1
mkfs.ext4 -F ${DEVICE}2

echo "✓ Partitions created"
echo ""

echo "📁 Mounting partitions..."

# Create mount points
mkdir -p /mnt/usb-boot
mkdir -p /mnt/usb-root

# Mount partitions
mount ${DEVICE}2 /mnt/usb-root
mkdir -p /mnt/usb-root/boot/efi
mount ${DEVICE}1 /mnt/usb-root/boot/efi

echo "✓ Partitions mounted"
echo ""

echo "🐧 Installing base system..."

# Install Debian base system
debootstrap --arch=amd64 bullseye /mnt/usb-root http://deb.debian.org/debian/

echo "✓ Base system installed"
echo ""

echo "📦 Copying application files..."

# Copy application
cp -r . /mnt/usb-root/opt/dvr-face-recognition/

echo "✓ Application files copied"
echo ""

echo "⚙️  Configuring system..."

# Configure fstab
cat > /mnt/usb-root/etc/fstab << EOF
${DEVICE}2 / ext4 defaults 0 1
${DEVICE}1 /boot/efi vfat defaults 0 2
EOF

# Configure hostname
echo "dvr-face-recognition" > /mnt/usb-root/etc/hostname

# Configure network
cat > /mnt/usb-root/etc/network/interfaces << EOF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
EOF

# Create startup script
cat > /mnt/usb-root/etc/rc.local << 'EOF'
#!/bin/bash
cd /opt/dvr-face-recognition
./start.sh &
exit 0
EOF

chmod +x /mnt/usb-root/etc/rc.local

echo "✓ System configured"
echo ""

echo "🥾 Installing bootloader..."

# Chroot and install GRUB
mount --bind /dev /mnt/usb-root/dev
mount --bind /proc /mnt/usb-root/proc
mount --bind /sys /mnt/usb-root/sys

chroot /mnt/usb-root /bin/bash << 'CHROOT_EOF'
apt-get update
apt-get install -y grub-efi-amd64 linux-image-amd64
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=DVR-FaceRec
update-grub
CHROOT_EOF

# Unmount
umount /mnt/usb-root/dev
umount /mnt/usb-root/proc
umount /mnt/usb-root/sys
umount /mnt/usb-root/boot/efi
umount /mnt/usb-root

echo "✓ Bootloader installed"
echo ""

echo "╔═══════════════════════════════════════════════════╗"
echo "║   Bootable USB Created Successfully! ✓            ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Safely remove the USB drive"
echo "2. Insert into target device"
echo "3. Boot from USB"
echo "4. System will auto-start on boot"
echo ""
echo "⚙️  Configuration:"
echo "   Edit /opt/dvr-face-recognition/config/config.json"
echo ""
