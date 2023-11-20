import argparse
import os

from rich import print as rprint
from tinytag import TinyTag

def walk_target_dir( dir: str ) -> list[str]:
    filelist = list()
    for root , ds , fs in os.walk( dir ):
        for f in fs:
            fullpath = os.path.join( root , f )
            filelist.append( fullpath )
    return filelist

def main():
    parser = argparse.ArgumentParser(
        prog = "mfm" ,
        description = "Windows Music Folder Manager Script"
    )
    parser.add_argument( '-d' , "--dir" , metavar = "DIR" , help = "Target Music Directory" , required = True )
    parser.add_argument( "--tracknum-width" , metavar = "WIDTH" , help = "Width of Tracknum" , required = False , type = int , default = 2 )
    args = parser.parse_args()

    target_dir = args.dir
    tracknum_width = args.tracknum_width

    if target_dir == os.curdir:
        rprint( "[red]Error:[/] Cannot run this script inside the target directory" )
        exit( 1 )

    if not os.path.exists( target_dir ):
        rprint( f"[red]Error:[/] Target Directory [magenta]\"{target_dir}\"[/] not found" )
        exit( 1 )
    
    filelist = walk_target_dir( target_dir )
    if len( filelist ) == 0:
        rprint( f"[red]Error:[/] Target Directory [magenta]\"{target_dir}\"[/] is empty" )
        exit( 1 )

    album_set = set()
    artist_set = set()
    samplerate_set = set()
    bitdepth_set = set()
    
    for file in filelist:
        if not TinyTag.is_supported( file ):
            rprint( f"[yellow]Warning:[/] File [magenta]\"{file}\"[/] cannot be recognized by Tinytag module" )
            continue

        rprint( f"[cyan]Processing File [magenta]\"{file}\"[/]...[/]" )
        tag = TinyTag.get( file )
        this_artist = tag.artist
        this_title = tag.title
        this_album = tag.album
        this_samplerate = tag.samplerate
        this_bitdepth = tag.bitdepth
        this_tracknum = tag.track
        rprint( 
f'''\t[yellow]title:[/] {this_title}
\t[yellow]artist:[/] {this_artist}
\t[yellow]album:[/] {this_album}
\t[yellow]tracknum:[/] {this_tracknum}
\t[yellow]samplerate/bitdepth:[/] {this_samplerate}Hz/{this_bitdepth}bit'''
        )
        new_filename = f"{this_tracknum:>0{tracknum_width}}. {this_title}{os.path.splitext( file )[1]}"
        rprint( f"[green]New Filename Generated:[/] [magenta]\"{new_filename}\"[/]" )
        confirm = input( "Comfirm / Rename: " )
        try:
            if len( confirm ) == 0:
                os.rename( file , os.path.join( os.path.dirname( file ) , new_filename ) )
            # confirmed
            else:
                os.rename( file , os.path.join( os.path.dirname( file ) , confirm ) )
            # needs to be changed
        except OSError as e:
            rprint( f"[red]Error:[/] Rename failed: {e}" )

        if this_artist not in artist_set:
            artist_set.add( this_artist )
        if this_album not in album_set:
            album_set.add( this_album )
        if this_samplerate not in samplerate_set:
            samplerate_set.add( this_samplerate )
        if this_bitdepth not in bitdepth_set:
            bitdepth_set.add( this_bitdepth )
    # rename all files

    rprint( f"[cyan]Processing Target Folder [magenta]\"{target_dir}\"[/]...[/]")

    if len( artist_set ) > 1:
        rprint( f"[yellow]multiple artists:[/] {artist_set}" )
        rprint( "[yellow]Please choose or input the artist to use in dirname: " , end = "" )
        artist_in_dirname = input()
    else:
        rprint( f"[yellow]artist:[/] {artist_set}[/]")
        artist_in_dirname = next( iter( artist_set ) )

    if len( artist_in_dirname ) != 0:
        artist_in_dirname = " - " + artist_in_dirname

    if len( album_set ) > 1:
        rprint( f"[yellow]multipule albums:[/]" )
        album_num = 1
        album_list = list( album_set )
        for album in album_list:
            rprint( f"\t{album_num}: [green]\"{album}\"[/]" )
            album_num += 1
        rprint( "[yellow]Please choose one album to use in dirname: " , end = "" )
        album_in_dirname = album_list[int(input())-1]        
    else:
        rprint( f"[yellow]album:[/] {album_set}" )
        album_in_dirname = next( iter( album_set ) )
    rprint( f"[green]Use album [magenta]\"{album_in_dirname}\"[/] in dirname" )

    if len( samplerate_set ) == 1 and len( bitdepth_set ) == 1:
        samplerate_in_dirname = next( iter( samplerate_set ) )
        bitdepth_in_dirname = next( iter( bitdepth_set ) )
        dirname_title = "[Hi-Res]" if ( int( samplerate_in_dirname ) > 44100 and int( bitdepth_in_dirname ) > 16 ) else "[CD]"
        write_sb_in_dirname = True
        rprint( f"[yellow]samplerate/bitdepth:[/] {samplerate_in_dirname}Hz/{bitdepth_in_dirname}bit" )
    else:
        rprint( "[red]Multiple samplerates or bitdepths in target directory, please judge them by yourself[/]" )
        write_sb_in_dirname = False
    
    new_target_dirname = f"{dirname_title} {album_in_dirname}{artist_in_dirname if len( artist_in_dirname ) != 0 else ''} [{samplerate_in_dirname/1000}kHz／{bitdepth_in_dirname}bit]"
    rprint( f"[green]New Target Directory Name Generated:[/] [magenta]\"{new_target_dirname}\"[/]" )
    confirm = input( "Comfirm / Rename: " )
    try:
        if len( confirm ) == 0:
            os.rename( target_dir , new_target_dirname )
        # confirmed
        else:
            os.rename( target_dir , confirm )
        # needs to be changed
    except OSError as e:
        rprint( f"[red]Error:[/] Rename failed: {e}" )

if __name__ == "__main__":
    main()