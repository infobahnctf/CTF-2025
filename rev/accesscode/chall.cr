def die(msg : String)
  puts msg
  exit 1
end

# slopped ts
@[AlwaysInline]
def base64_decode(input : String) : Bytes
  # Obfuscated alphabet - built programmatically
  k = 0x47_u8
  charset = String.build do |str|
    # Build A-Z
    26.times { |n| str << (((n + 0x41) ^ k) ^ k).chr }
    # Build a-z
    26.times { |n| str << (((n + 0x61) ^ k) ^ k).chr }
    # Build 0-9
    10.times { |n| str << (((n + 0x30) ^ k) ^ k).chr }
    # Special chars
    str << ((0x2B ^ k) ^ k).chr  # +
    str << ((0x2F ^ k) ^ k).chr  # /
  end

  # Build lookup with obfuscated indexing
  tbl = Hash(Char, Int32).new
  idx = 0
  charset.each_char do |ch|
    tbl[ch] = idx
    idx = idx + 1
  end

  # Remove noise
  clean = input.gsub(/\s/, "")
  pad_cnt = clean.count('=')

  # Calculate size with extra step
  sz = (clean.size * 3) // 4
  sz = sz - pad_cnt
  buf = Bytes.new(sz)

  # Process with modified flow
  pos = 0
  offset = 0
  while offset < clean.size
    # Extract values
    vals = StaticArray(Int32, 4).new(0)
    4.times do |idx|
      if offset + idx < clean.size
        ch = clean[offset + idx]
        vals[idx] = ch == '=' ? 0 : tbl[ch]
      end
    end

    # Reconstruct bytes with bit manipulation
    tmp1 = (vals[0] << 2) | (vals[1] >> 4)
    tmp2 = ((vals[1] & 15) << 4) | (vals[2] >> 2)
    tmp3 = ((vals[2] & 3) << 6) | vals[3]

    # Store with bounds checking
    if pos < sz
      buf[pos] = tmp1.to_u8
      pos += 1
    end
    if pos < sz
      buf[pos] = tmp2.to_u8
      pos += 1
    end
    if pos < sz
      buf[pos] = tmp3.to_u8
      pos += 1
    end

    offset += 4
  end

  buf
end

STDOUT.sync = true
print "Enter the access code: "
code = gets
die("Bad access code.") if code.nil? || code.size != 96 * 2 || code.match(/[^a-z0-9]/i)

# i stole this algorithm from a roblox script :sob:
swapped = code[96..] + code[...96]
data = swapped.gsub(/../) { |match| match.to_i(16).chr }.to_slice

2.times do
  text = String.new(data)
  rotated = text.chars.map do |c|
    case c
    when 'a'..'z'
      (((c - 'a') + 13) % 26 + 'a'.ord).chr
    when 'A'..'Z'
      (((c - 'A') + 13) % 26 + 'A'.ord).chr
    else
      c
    end
  end.join

  reversed = rotated.reverse

  begin
    decoded = base64_decode(reversed)
  rescue exception
    die("Bad access code.")
  end

  key1 = "gGIghgQHUGadFAHVGFIUsaddwg".to_slice
  key2 = "DBDabASsjnBajhvjhDShuGdvW".to_slice

  data = Bytes.new(decoded.size) do |i|
    decoded[i] ^ key1[i % key1.size] ^ key2[i % key2.size]
  end
end

result = String.new(data)

if result =~ /[^\x20-\x7e]/
  die("Bad access code.")
elsif result[...15] == "Usage: ./chall "
  puts "Welcome " + `#{result[15..]}`
else
  puts "Welcome " + result
end