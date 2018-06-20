def main():

    fh = open("/home/student/files/rt_trips_2017_I_DB.txt", 'r')

    for line in fh:

        route = line.split(';')[3]

        if route not in open("trips_id.txt").read():

            fh2 = open("trips_id.txt", 'a')

            fh2.write(route)
            fh3 = open("trips_route/" + route + ".txt", 'a+')

            fh3.write(line)

            fh2.close()
            fh3.close()

        else:

            fh3 = open("trips_route/" + route + ".txt", 'a+')

            fh3.write(line)
            fh3.close()


if __name__ == "__main__":
    main()



