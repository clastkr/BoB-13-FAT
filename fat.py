import struct
import sys

def extract_bpb(file):
    file.seek(0)
    bpb_content = file.read(36)
    bytes_per_sector, sectors_per_cluster, reserved_sectors, num_fats = struct.unpack_from('<HBHB', bpb_content, 11)
    file.seek(36)
    fat_size_32 = struct.unpack_from('<I', file.read(4))[0]
    fat_start = reserved_sectors * bytes_per_sector
    fat_size = fat_size_32 * bytes_per_sector
    return fat_start, fat_size

def get_fat_entries(file, start, length):
    file.seek(start)
    fat_content = file.read(length)
    return struct.unpack_from('<' + 'I' * (length // 4), fat_content)

def find_cluster_chain(fat_entries, initial_cluster):
    chain = []
    current_cluster = initial_cluster
    while current_cluster < 0x0FFFFFF8:
        chain.append(current_cluster)
        next_cluster = fat_entries[current_cluster] & 0x0FFFFFFF
        if next_cluster == 0 or next_cluster >= len(fat_entries):
            break
        current_cluster = next_cluster
    return chain

def run():

    disk_image = sys.argv[1]
    initial_cluster = int(sys.argv[2])

    with open(disk_image, 'rb') as file:
        fat_start, fat_length = extract_bpb(file)

        if fat_length == 0:
            sys.exit(1)

        fat_entries = get_fat_entries(file, fat_start, fat_length)
        cluster_chain = find_cluster_chain(fat_entries, initial_cluster)

        print(" ".join(map(str, cluster_chain)))

if __name__ == "__main__":
    run()
